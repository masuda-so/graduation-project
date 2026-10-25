#!/usr/bin/env python3
"""User-operated pilot setup. No package installation or paid calls on import."""
import argparse
import csv
import datetime as dt
import getpass
import hashlib
import json
import os
import signal
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / 'pilot'
REPOS = json.loads((PILOT / 'repos.json').read_text())


def stamp():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def read_data():
    path = PILOT / 'data/comments.json'
    rows = json.loads(path.read_text())
    if not isinstance(rows, list) or not 15 <= len(rows) <= 30:
        raise ValueError('初回試験は15〜30件の配列にしてください。')
    ids = []
    for row in rows:
        for field in ('id', 'speaker', 'text'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError('id/speaker/text は空でない文字列が必要です。')
        ids.append(row['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('id が重複しています。')
    return rows


def prepare():
    rows = read_data()
    data = PILOT / 'data'
    for name, header, fields in (
        ('kouchou.csv', ['comment-id', 'comment-body'], ['id', 'text']),
        ('tttc.csv', ['id', 'interview', 'comment'], ['id', 'speaker', 'text']),
    ):
        # CSVs are derived artifacts; comments.json remains the authoritative input.
        with (data / name).open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(header)
            writer.writerows([[r[k] for k in fields] for r in rows])
    for name, header in (('kouchou.csv', ['comment-id', 'comment-body']),
                         ('tttc.csv', ['id', 'interview', 'comment'])):
        with (data / name).open(encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == header
            exported = list(reader)
        assert len(exported) == len(rows)
        assert [list(r.values())[0] for r in exported] == [r['id'] for r in rows]
        assert [list(r.values())[-1] for r in exported] == [r['text'] for r in rows]
    print(f'同一の {len(rows)} 件から両CSVを生成・照合しました。API呼び出しなし。')


def repo_path(tool):
    return ROOT / 'vendor' / REPOS[tool]['directory']


def output(cmd, cwd=None):
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def verify_repo(tool):
    p = repo_path(tool)
    if not (p / '.git').is_dir():
        raise RuntimeError(f'先に fetch を実行してください: {p}')
    if output(['git', 'remote', 'get-url', 'origin'], p) != REPOS[tool]['url']:
        raise RuntimeError('既存リポジトリのoriginが異なるため停止しました。')
    if output(['git', 'rev-parse', 'HEAD'], p) != REPOS[tool]['sha']:
        raise RuntimeError('コミットが固定版と異なります。既存の作業は変更しません。')
    if output(['git', 'diff', 'HEAD', '--name-only'], p):
        raise RuntimeError('追跡ファイルに変更があります。研究用の元コードとの混同を防ぐため停止します。')
    return p


def fetch():
    (ROOT / 'vendor').mkdir(exist_ok=True)
    for tool, meta in REPOS.items():
        dest = repo_path(tool)
        if not dest.exists():
            subprocess.run(['git', 'clone', '--filter=blob:none', '--no-checkout',
                            '--no-tags', meta['url'], str(dest)], check=True)
            subprocess.run(['git', 'checkout', '--detach', meta['sha']], cwd=dest, check=True)
        verify_repo(tool)
        print(f'{tool}: {meta["sha"]}')
    prepare()


def pnpm():
    if shutil.which('corepack'):
        return ['corepack', 'pnpm']
    if shutil.which('pnpm'):
        return ['pnpm']
    raise RuntimeError('Corepack または pnpm 10.26.0 を準備してください。')


def measured(label, commands, cwd=None, env=None, base=None):
    base = base or ROOT / 'pilot-results/setup'
    run = base / (stamp() + '-' + label + '-' + uuid.uuid4().hex[:6])
    run.mkdir(parents=True)
    started = time.monotonic()
    code = 1
    try:
        with (run / 'console.log').open('w') as log:
            for cmd in commands:
                # Commands never contain an API key; only child environment does.
                print('実行:', ' '.join(map(str, cmd)), flush=True)
                log.write('\nCOMMAND ' + ' '.join(map(str, cmd)) + '\n')
                log.flush()
                process = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, text=True, errors='replace',
                                           start_new_session=True)
                try:
                    for line in process.stdout:
                        print(line, end='', flush=True)
                        log.write(line)
                    code = process.wait()
                except KeyboardInterrupt:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    code = 130
                    raise
                if code:
                    raise subprocess.CalledProcessError(code, cmd)
    finally:
        (run / 'timing.json').write_text(json.dumps({
            'label': label, 'seconds': time.monotonic() - started,
            'exit_code': code, 'utc': stamp(),
        }, indent=2))
        print(f'ログ: {run}')
    return run


def install(tool):
    repo = verify_repo(tool)
    if tool == 'kouchou':
        py = os.environ.get('PILOT_PYTHON', 'python3.12')
        version = json.loads(output([py, '-c', 'import sys,json;print(json.dumps(list(sys.version_info[:2])))']))
        if tuple(version) < (3, 12):
            raise RuntimeError('Python 3.12以上が必要です。')
        venv = ROOT / '.venvs/kouchou'
        measured('install-kouchou', [
            [py, '-m', 'venv', str(venv)],
            [str(venv / 'bin/python'), '-m', 'pip', 'install', '-e',
             str(repo / 'packages/analysis-core') + '[clustering]'],
            [str(venv / 'bin/python'), '-m', 'pip', 'freeze'],
        ])
    else:
        major = int(output(['node', '-p', 'process.versions.node.split(".")[0]']))
        if major < 25:
            raise RuntimeError('固定版のルート要件はNode.js 25以上です。nvm等で切り替えてください。')
        cli = pnpm()
        version = output(cli + ['--version'], repo)
        if version != '10.26.0':
            raise RuntimeError(f'pnpm 10.26.0が必要です。現在: {version}')
        measured('install-tttc', [cli + ['install', '--frozen-lockfile'],
                                 cli + ['--filter=tttc-common', 'run', 'build']], cwd=repo)


def run_tool(tool, plan):
    repo = verify_repo(tool)
    prepare()
    env = dict(os.environ)
    if not plan and not env.get('OPENAI_API_KEY'):
        env['OPENAI_API_KEY'] = getpass.getpass('OpenAI API key（非表示・ファイル保存なし）: ')
        if not env['OPENAI_API_KEY'].strip():
            raise ValueError('APIキーが空です。')
    model = env.get('PILOT_MODEL', 'gpt-4o-mini')
    run = ROOT / 'pilot-results' / (stamp() + '-' + tool + '-' + uuid.uuid4().hex[:6])
    run.mkdir(parents=True)
    raw = (PILOT / 'data/comments.json').read_bytes()
    (run / 'input.json').write_bytes(raw)
    metadata = {'tool': tool, 'mode': 'plan' if plan else 'live', 'model': model,
                'source': REPOS[tool], 'input_sha256': hashlib.sha256(raw).hexdigest(),
                'n': len(read_data()), 'synthetic': True, 'full_web_app': False,
                'python': sys.version, 'utc': stamp()}
    (run / 'manifest.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    if tool == 'kouchou':
        config = {
            'name': '人工20件・導入比較', 'question': '公園の照明とベンチ整備について、どのような意見がありますか？',
            'input': 'kouchou', 'model': model, 'provider': 'openai',
            'is_embedded_at_local': False,
            'embedding': {'model': 'text-embedding-3-small'},
            'extraction': {'workers': 1, 'limit': len(read_data())},
            'hierarchical_clustering': {'cluster_nums': [2, 4]},
        }
        config_path = run / 'pilot.json'
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))
        cmd = [str(ROOT / '.venvs/kouchou/bin/kouchou-analyze'), '--config', str(config_path),
               '--input-dir', str(PILOT / 'data'), '--output-dir', str(run / 'artifacts')]
        if plan:
            cmd.append('--dry-run')
    else:
        env['PILOT_MODEL'] = model
        cmd = pnpm() + ['exec', 'tsx', str(PILOT / 'tttc-pilot.ts'),
                        str(run / 'input.json'), str(run / 'artifacts')]
        if plan:
            cmd.append('--check-input')
        repo = repo / 'pipeline-worker'
    measured(('plan-' if plan else 'run-') + tool, [cmd], cwd=repo, env=env, base=run / 'logs')
    print(f'結果: {run}')


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('fetch')
    sub.add_parser('prepare')
    for action in ('install', 'run'):
        p = sub.add_parser(action)
        p.add_argument('tool', choices=REPOS)
        if action == 'run':
            p.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    if args.action == 'fetch': fetch()
    elif args.action == 'prepare': prepare()
    elif args.action == 'install': install(args.tool)
    else: run_tool(args.tool, args.plan)


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as exc:
        print(f'停止: {exc}', file=sys.stderr)
        sys.exit(1)

# リポジトリガイドライン

## プロジェクト構成とモジュールの配置

慶應 SFC 卒業プロジェクト 2 の研究リポジトリ。広聴AI（kouchou-ai）の処理のどの段階で少数の理由が失われるかを、文化庁パブリックコメントで段階別に検証する。

- `docs/`（計画とメモ。日程の正本は `docs/スケジュール.md`。`docs/private/` は内部メモで未コミット）。
- `literature/`（先行研究リスト、調査確認、資料索引 `sources-index.md`。`literature/sources/` は第三者の著作物で未コミット・読み取り専用）。
- `experiments/<日付-内容>/`（`config.json`、`inputs/`、`outputs/`、`diagnostics/`。実データの原文と診断ファイルはコミットしない）。`experiments/trial-2026-10-17-pypi/` は初回動作確認で、研究の結果ではない。
- `pilot/`（導入試験の補助コード）、`vendor/kouchou-ai`（固定コミット `eb38328d` の submodule。編集しない）、`.venv/`（uv の仮想環境）。

## ビルド・テスト・開発コマンド

- `uv venv .venv --python 3.12` と `uv pip install --python .venv/bin/python -e "vendor/kouchou-ai/packages/analysis-core[embeddings,clustering]"` — 環境の作成。`pip` を直接使わない。
- `.venv/bin/kouchou-analyze --config experiments/<実行名>/config.json --input-dir experiments/<実行名>/inputs --output-dir experiments/<実行名>/outputs --dry-run` — 事前確認。`--dry-run` を外した実行は本人が行う。
- CI（`Offline checks`）: `python -m compileall -q pilot`、追跡中の JSON の読み込み、日英 README の見出し数の一致。

## コーディングスタイルと命名規則

- Python は PEP 8（4 スペース）。`.editorconfig` が文字コードと改行を揃える。
- 文書は `docs/` に日付付きのファイル名で置き、既存ファイルの更新は末尾に「YYYY-MM-DD 追記」の節を足す。
- 実験結果は実行フォルダ内に置き、プロジェクト直下に `outputs/` や `config.json` を作らない。

## テストの指針

- 検証できる変更を優先する: 手順や設定の変更は `--dry-run` で確認し、出力の形（ファイル名と件数）を記録する。注釈や集計の変更は件数と抜き取り確認を添える。
- 高価な処理は小さな入力（予備実験の 30 件）で先に動かす。本実験は各条件 5 回、乱数の種は固定せず条件を記録する。
- 有料 API（OpenAI、`gpt-4o-mini`）は費用を見積もる（目安: 100 件 × 15 回で約 0.74 ドル）。

## コミットとプルリクエストの指針

- コミットは git 公式ガイドの形: 1 行目は 50 文字以内を目安にした要約、空行、本文（何を・なぜ、72 桁前後で折り返す）、空行、トレーラー。作者は `masudaso <258961222+masuda-so@users.noreply.github.com>`、SSH 署名付き（ルールセットで署名必須）。
- 初回コミットだけ author と committer の日時をその日の `00:00:00 +0900` に揃える。2 回目以降は実際の日時。
- AI が内容を書いたコミットには、関わったエージェントごとに GitHub 公式書式のトレーラーを 1 行ずつ付ける: `Co-authored-by: Codex <noreply@openai.com>`、`Co-authored-by: Claude Fable 5.1 <noreply@anthropic.com>`（モデル名は作業したもの）。大文字小文字は公式どおり `Co-authored-by:`。
- 公開済みの履歴は書き換えない。やむを得ない場合は本人が判断し `--force-with-lease` を使う。
- main への変更は PR 経由（直接 push 不可）。PR の題名・説明・レビューコメントは日本語を基本とし、利用者が別の言語を指定した場合はそれを優先する。説明には変更内容と検証結果を書く。`Offline checks` が必須チェック。
- `README.md`（日本語）と `README.en.md`（英語）は冒頭で相互リンクし、5 見出し（概要・主な機能と制約・導入と使い方・サポートと関連資料・開発と貢献）を揃え、仕様・手順・制約の変更は同じ PR で両方を更新する。未実装・未検証の内容を利用可能と書かない。
- ライセンスはコードが MIT（`LICENSE`）、文書・図・注釈データが CC BY 4.0（`LICENSE-CC-BY-4.0`）。新しいファイルもこの区分に従う。

## セキュリティと設定の注意

- 第三者の著作物（`literature/sources/`、実データの原文、`experiments/*/diagnostics/`）と内部メモ（`docs/private/`）はコミットしない（`.gitignore` 済み）。API キーを置かない。
- データの削除、日程の変更、注釈規則や評価指標（カバー率）の定義変更、費用のかかる実行の前に本人に確認する。

## エージェント向けの指示

- 本人の指示なしに、コードの実装・インストール・実行・クローン・コミット・push をしない。提案と手順の説明はしてよい。
- 対象ツールは広聴AI のみ。固定コミットの公式 CLI をそのまま使い、研究コード（注釈・判定・集計）はパイプラインの外側に置く。ラベル付けの `sampling_num` は Web アプリに合わせて 30。注釈は AI で下書きし、人が 1 件ずつ確認する。
- 最初に読むもの: `docs/スケジュール.md`（日程を変えたら同じファイルを更新）、`docs/卒論の進め方と書き方_2026-10-15.md`、`docs/第1回発表_振り返り_2026-10-26.md`（カバー率の定義）、`docs/注釈ガイド_v0_2026-10-25.md`。
- 作業報告、Issue や PR へのコメントは日本語を基本とする。コード識別子、ファイル名、コマンド、ログやエラーの引用は原文のまま残し、説明を日本語で添える。
- 言語の統一を理由に既存のコミット履歴や他者のコメントを書き換えない。投稿・コミット・push の許可は別途の作業指示に従う。

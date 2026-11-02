# AIによる意見集約は少数の理由をどこで失うか

[日本語](README.md) | [English](README.en.md)

## 概要

広聴AI（kouchou-ai）の処理（抽出 → クラスタ → ラベル付け → 全体要約）のどの段階で、入力の中で出現頻度が低い理由・条件が、頻度の高い理由と比べてどの段階で失われるかを、文化庁「AIと著作権に関する考え方について（素案）」パブリックコメントを用いて段階別に検証する研究です。慶應義塾大学 湘南藤沢キャンパス（SFC）環境情報学部の科目「卒業プロジェクト2」（2026年度秋学期）の研究成果物として作成する。著者は増田創。

状態：計画段階（2026-10-20時点）。第1回進捗発表 2026-10-26、成果登録締切 2027-02-01。

ライセンス：コード（`pilot/`、今後の注釈・集計スクリプト）は MIT（`LICENSE`）、文書・図・注釈データ（`docs/`、`literature/`、`experiments/` の生成物）は CC BY 4.0（`LICENSE-CC-BY-4.0`）。引用時は So Masuda と本リポジトリを出典として示す。

## 主な機能と制約

- 広聴AIは固定コミット `eb38328d6cc9b93c767ff81fe28c3d518fc03ff8` の公式CLI（`packages/analysis-core`）を改変せずに使う。研究用コードはパイプラインの外側（注釈・判定・集計）にとどめる。
- 条件は一度に1つだけ変え（抽出プロンプト、ラベル用サンプル数）、各条件を5回実行して揺れを幅で示す。乱数の種は固定しない。
- 入力データの意見文は投稿者の著作物のため、このリポジトリには含めない。使用した受付番号と注釈ラベルのみを公開し、原文は文化庁サイトから再取得する。
- 第三者の資料（論文PDF、他リポジトリのスナップショット）も含めない。`literature/sources-index.md` に入手元とSHA-256を記録している。
- 主張しないこと：新手法の優位性、全自治体・全モデルへの一般化、社会的少数者の代表。

## 導入と使い方

1. 広聴AIを固定コミットで取得し、専用の仮想環境に editable install する。

   ```bash
   git clone https://github.com/digitaldemocracy2030/kouchou-ai.git vendor/kouchou-ai
   git -C vendor/kouchou-ai checkout --detach eb38328d6cc9b93c767ff81fe28c3d518fc03ff8
   uv venv .venv --python 3.12
   uv pip install --python .venv/bin/python -e "vendor/kouchou-ai/packages/analysis-core[embeddings,clustering]"
   ```

2. `experiments/<実行名>/` に `config.json` と `inputs/<名前>.csv`（列は `comment-id`, `comment-body`）を置く。
3. 事前確認してから実行する。

   ```bash
   .venv/bin/kouchou-analyze --config experiments/<実行名>/config.json --input-dir experiments/<実行名>/inputs --output-dir experiments/<実行名>/outputs --dry-run
   ```

4. `outputs/` の `args.csv`、`relations.csv`、`hierarchical_clusters.csv`、`hierarchical_*_labels.csv`、`hierarchical_overview.txt` を段階ごとの判定に使う。

`experiments/trial-2026-10-17-pypi/` は、PyPI版・公式ガイドの例文5件・gpt-4o-mini による初回動作確認の記録で、研究の結果ではない。

## サポートと関連資料

### リポジトリ構成

| フォルダ・ファイル | 中身 |
|---|---|
| `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` | 作業を手伝うAIエージェント向けの約束（`CLAUDE.md` と `GEMINI.md` は `AGENTS.md` を読み込むだけ） |
| `docs/` | 計画・メモ。日程の正本は `docs/スケジュール.md`。`docs/private/` は内部メモで未コミット |
| `literature/` | 先行研究リスト、研究領域の地図、調査メモ、資料索引。`literature/sources/` は手元のみ（読み取り専用、未コミット） |
| `experiments/` | 実験の設定・入力・出力。1回の実行ごとに `experiments/<日付-内容>/` |
| `pilot/` | 導入試験用の補助コード（Codex作成） |
| `vendor/kouchou-ai` | 広聴AIのクローン（上記コミット、detached HEAD）。編集しない |

### 関連資料

- 広聴AI：https://github.com/digitaldemocracy2030/kouchou-ai （AGPL-3.0）
- 入力データ：文化庁 文化審議会著作権分科会 法制度小委員会（第7回）配付資料 https://www.bunka.go.jp/seisaku/bunkashingikai/chosakuken/hoseido/r05_07/
- 先行研究の一覧：`literature/先行研究リスト_2026-10-15.md`
- 第三者の資料・データの扱い：[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

問い合わせは GitHub の Issue へ。

## 開発と貢献

個人の卒業研究のため、外部からの変更は受け付けていない。誤りの指摘は Issue で受け付ける。日程・方針・エージェントの作業規則は `docs/スケジュール.md` と `AGENTS.md` を参照。

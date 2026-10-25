# 広聴AI・TttCの小規模導入試験

2026年10月15日作成。**本人が以下のコマンドを実行するためのコード**です。Codexは上流ソースの確認と、この補助コードの作成・ローカル構文検査を行いました。リポジトリの取得、依存関係のインストール、有料APIを使う分析はまだ実行していません。

## 今回動かす範囲

- 広聴AI：公式 `analysis-core` のCLI。通常の階層分析を実行し、CSV／JSON／要約／補助HTMLを保存。
- TttC：上流の `commentsToTree` → `extractClaims` → `sortAndDeduplicateClaims` → `generateTopicSummaries` を呼ぶ補助ランナー。上流の既定プロンプトに日本語出力の指示を追加し、その全文も保存。
- TttCは公式の分析関数を使いますが、**Webアプリ全体の再現ではありません**。認証、ジョブキュー、Redis/GCSへの永続化、画面、bridging、crux生成は今回の対象外です。Webアプリの導入負荷は、別途必要なクラウド設定を含めて区別してください。
- どちらもクラウド上のOpenAI APIを使います。試験を開始すると入力20件がAPIへ送られ、課金が発生します。API利用の金額上限はこの補助コードでは保証しません。
- 最終出力は、広聴AIが全体概要、今回のTttCランナーが話題別要約です。同じ粒度の要約同士の品質比較ではありません。

固定する上流コミット：

| ツール | コミット |
|---|---|
| 広聴AI | `eb38328d6cc9b93c767ff81fe28c3d518fc03ff8` |
| TttC | `be96a2bc0cd56aaecc0aa10d5981bebcea8b5b6e` |

この時点のCLI／型定義／公式の分析関数を読んで作成しています。上流が進んでも自動で追従しません。取得済みフォルダが違うorigin・コミット・追跡ファイルの変更を持つ場合は、上書きせず止まります。

## 1. コードをプロジェクトに持ってくる

ターミナルで次を実行してください。

```bash
cd "$HOME/Desktop/Graduation Project"
python3 pilot/manage.py fetch
```

`vendor/kouchou-ai` と `vendor/tttc-light-js` に取得します。上流はdetached HEADで固定し、ブランチ作成・コミット・pushはしません。`pilot/data/comments.json` から両方用のCSVも生成して、ID・本文・件数が同じか確認します。この段階ではパッケージのインストールもAPI呼び出しもありません。

入力は公園整備に関する**人工20件**です。全員架空で、条件付き賛成や異なる理由を含めています。自治体のパブコメや世論の標本ではなく、導入確認専用です。実データを使う本実験用の取り込み・標本化は、別に設計します。

## 2. PythonとNodeの準備

広聴AIにはPython 3.12以上、固定したTttCルートにはNode 25以上とpnpm 10.26.0が必要です。確認時、この端末のPATHにはPython 3.12がなく、Nodeは24系でした。ターミナルの設定や別環境では異なる可能性があります。

Homebrewとnvmを既に使っている場合の例：

```bash
brew install python@3.12
source "$HOME/.nvm/nvm.sh"
nvm install 25
nvm use 25
python3.12 --version
node --version
```

`brew`／`nvm`が存在しない場合はここで止めてください。新しい環境管理ツールをさらに導入する手順はこのコードに含めていません。別のPythonを使うときは、`PILOT_PYTHON=/そのPythonの絶対パス` を指定できます。Node 26など25以上が既に利用できれば、25を追加する必要はありません。

TttC側はCorepackがあればリポジトリの `packageManager` に従ってpnpmを使用します。Corepackがない場合はpnpm 10.26.0を別途準備します。

## 3. 依存関係を導入する（API呼び出しなし）

```bash
cd "$HOME/Desktop/Graduation Project"
python3 pilot/manage.py install kouchou
python3 pilot/manage.py install tttc
```

広聴AIはプロジェクト専用の `.venvs/kouchou` を作り、取得したソースをeditable installします。埋め込みはOpenAI APIを使う設定なので、ローカル埋め込み用のTorchは追加せず、`clustering` extrasを導入します。

TttCは公式の `pnpm install --frozen-lockfile` と共通パッケージのビルドを行います。分析だけの試験でも、今回は上流のworkspace依存関係を利用するため、フロントエンドを含む依存解決が発生します。依存先のインストールスクリプトも通常どおり動作します。

導入時間とコンソール出力は `pilot-results/setup/` に保存します。これは実際のコマンド所要時間で、事前の環境準備・手作業・エラーを調べた時間は含みません。別途メモしてください。

## 4. APIを使わない確認

```bash
python3 pilot/manage.py run kouchou --plan
python3 pilot/manage.py run tttc --plan
```

広聴AIはCLIのdry-run、TttCは公式モジュールのimportと入力形式の確認です。**検査の範囲は同一ではありません**。どちらもAPIキーの正しさや実際の生成成功までは確認しません。

## 5. 同じ入力を実際に分析する（API課金あり）

```bash
python3 pilot/manage.py run kouchou
python3 pilot/manage.py run tttc
```

各コマンドがAPIキーを非表示で尋ねます。キーをコード・設定ファイル・コマンド履歴に書く必要はありません。既に環境変数 `OPENAI_API_KEY` があればそれを使います。既定のLLMモデルは両方 `gpt-4o-mini`。変更する場合は、両方の上流コード・APIアカウントがそのモデルを扱えることを確認して、同じ `PILOT_MODEL` を設定してください。

広聴AIでは別に埋め込みAPI（`text-embedding-3-small`）も使います。TttCとは分類方法・プロンプト・生成量・API方式が異なるので、同じLLM名を指定しても計算量が揃うわけではありません。TttC既定指示は、逸話や明確な立場のない文を抽出しないなどの選択規則を含みます。これは導入確認後に研究上検討する対象であり、今回は黙って書き換えません。

実行ごとに新しい出力先を作ります。途中までの出力は残りますが、このランナーでの再実行は原則最初からで、追加課金が発生します。失敗時はログを見てから判断してください。中断はCtrl+Cです。すでに処理されたAPI呼び出しの課金は取り消されません。

## 中間出力の場所

`pilot-results/<UTC日時>-<ツール>-<識別子>/` に保存します。両方とも同じ入力JSONのコピー、SHA-256、固定コミット、モデル、計画確認／実分析の区別を `manifest.json` に記録します。

| 確認対象 | 広聴AI `artifacts/pilot/` | TttC `artifacts/` |
|---|---|---|
| 初期の話題構造 | 抽出の後にクラスタを作るため、同等の前処理はない | `01-taxonomy.json` |
| 抽出された主張 | `args.csv` | `02-claims.json` |
| グループ・集約 | `hierarchical_clusters.csv`、`hierarchical_initial_labels.csv`、`hierarchical_merge_labels.csv` | `03-grouped-claims.json` |
| 要約 | `hierarchical_overview.txt` | `04-topic-summaries.json`、`summaries.txt` |
| 最終表示用データ | `hierarchical_result.json`、`report.html` | この補助ランナーではWebレポート形式には変換しない |
| 実行情報 | `hierarchical_status.json`、`logs/` | `metrics.json`、`prompts.json`、`run.json`、`logs/` |

順序は同じではありません。広聴AIは抽出→埋め込み→クラスタ→ラベル・概要、TttCは話題体系→主張抽出→統合→話題別要約です。対応のない工程を無理に同じ工程として採点しません。

TttCの `id-trace.csv` は、元コメントIDが抽出／統合後に現れるかだけを示します。重複として保存されている引用も含めます。**IDが残ることは、理由・条件の意味が保持された証明ではありません。** 広聴AIではまず `args.csv` のID列・本文列を実物で確認してから、同じ対応表を作ります。

TttCの `metrics.json` の費用は上流コード内の価格表に基づく概算です。請求額ではありません。使用量も失敗した呼び出し・リトライ分まで完全に把握できるとは限らないので、最終的な費用はAPI側の利用状況と照合します。

## 比較して決めること

| 項目 | 自分で記録する内容 |
|---|---|
| 導入負荷 | 環境準備の手作業時間、導入コマンド時間、エラーと解決方法、必要なサービス |
| 追跡可能性 | 原文IDから抽出文・集約文に戻れるか。条件の脱落を人が判断できるか |
| 再現性 | 同じコミット・入力・設定を保存できたか。再実行できるか |
| 実行負荷 | 実測時間、トークン、API利用状況、失敗した工程 |
| 改変範囲 | 自分の補助コードと、上流コードの境界を説明できるか |

まず20件の1回ずつで採用候補を絞ります。生成が1回成功しただけで、品質や少数意見保持の優劣は結論づけません。導入比較後、実データの予備実験で注釈単位・評価可能性を確認します。

## 参照した上流ファイル

- [広聴AI CLIガイド（固定版）](https://github.com/digitaldemocracy2030/kouchou-ai/blob/eb38328d6cc9b93c767ff81fe28c3d518fc03ff8/docs/user-guide/cli-quickstart.md)
- [広聴AI analysis-core](https://github.com/digitaldemocracy2030/kouchou-ai/tree/eb38328d6cc9b93c767ff81fe28c3d518fc03ff8/packages/analysis-core)
- [TttC分析ステップ](https://github.com/AIObjectives/tttc-light-js/tree/be96a2bc0cd56aaecc0aa10d5981bebcea8b5b6e/pipeline-worker/src/pipeline-steps)
- [TttC公式runner](https://github.com/AIObjectives/tttc-light-js/blob/be96a2bc0cd56aaecc0aa10d5981bebcea8b5b6e/pipeline-worker/src/pipeline-runner/runner.ts)
- [TttC既定プロンプト](https://github.com/AIObjectives/tttc-light-js/blob/be96a2bc0cd56aaecc0aa10d5981bebcea8b5b6e/common/prompts/index.ts)

上流のライセンスを保持したまま取得します。今回の補助コードは上流のファイルを編集しません。

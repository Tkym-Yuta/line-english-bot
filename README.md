# LINE English Test Grading Bot

LINEで送られた英単語テストの答案画像をOCRし、Geminiで採点して、結果をLINEに返信するアプリです。テストIDと出題単語はGoogle Sheetsで管理し、採点結果と復習対象の単語もSheetsへ保存します。

## Features

- LINE Messaging API の webhook で答案画像を受信
- Gemini による Test ID 読み取り、答案OCR、採点
- Google Sheets からテスト情報を取得
- 採点結果、間違えた単語、復習対象を Google Sheets に保存
- Cloud Run でのコンテナ実行に対応
- CLIで英単語テストを生成

## Architecture

```text
LINE
  |
  v
Cloud Run / FastAPI webhook
  |
  +-- LINE画像ダウンロード
  +-- Gemini OCR / 採点
  +-- Google Sheets 読み書き
  |
  v
LINEへ採点結果を返信
```

主な入口は `webhook.py` です。

## Repository Files

GitHubに載せる主なファイル:

```text
README.md
Dockerfile
.dockerignore
.gcloudignore
.gitignore
.env.example
requirements.txt
webhook.py
generate_test.py
config.example.py
services/
usecases/
models/
```

GitHubに載せないファイル:

```text
.env
config.py
credentials.json
TARGET1900.csv
TARGET1900.csv.rtf
answers/
outputs/
outputs_verify/
wrong_words.csv
*.log
__pycache__/
.DS_Store
.vscode/
```

`TARGET1900.csv` はアプリ実行には必要ですが、公開リポジトリには含めない想定です。Cloud Runへデプロイする場合は `.gcloudignore` でアップロード対象に含めるか、別の安全なデータ配置方法を使います。

## Environment Variables

`.env` または Cloud Run の環境変数に以下を設定します。

```text
LINE_CHANNEL_ACCESS_TOKEN=...
GEMINI_API_KEY=...
SPREADSHEET_ID=...
```

ローカルでは `.env.example` を参考に `.env` を作成します。

ローカルで `credentials.json` を使う場合はプロジェクト直下に置きます。本番のCloud Runでは、サービスアカウントに対象スプレッドシートを共有する構成を推奨します。

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

FastAPIをローカル起動します。

```bash
uvicorn webhook:app --reload --port 8080
```

ヘルスチェック:

```bash
curl http://localhost:8080/
```

## Cloud Run Deploy

```bash
gcloud run deploy line-english-bot \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars LINE_CHANNEL_ACCESS_TOKEN=xxx,GEMINI_API_KEY=xxx,SPREADSHEET_ID=xxx
```

デプロイ後、LINE Developers の Webhook URL に以下を設定します。

```text
https://<cloud-run-url>/callback
```

Google Sheets API と Google Drive API も有効化してください。

```bash
gcloud services enable sheets.googleapis.com
gcloud services enable drive.googleapis.com
```

## Google Sheets

以下のシートを使います。

```text
Tests
Submissions
WrongWords
```

Cloud Run のサービスアカウントをスプレッドシートの編集者として共有してください。

## Development Notes

- `generate_test.py` はテスト生成用CLIです。
- `webhook.py` はCloud Runで動かす本番入口です。
- `.env`、Google認証ファイル、出力ファイル、答案画像はコミットしません。
- 本番ログには答案OCR全文やGeminiの生レスポンスを出さないようにしています。

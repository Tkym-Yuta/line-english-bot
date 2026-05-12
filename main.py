import os
import json
from flask import Flask, request, abort

# --- services ---
from services.line_service import reply_message, push_message
from services.sheets_service import get_words
from usecases.generate_test import generate_test, format_test
from usecases.grade_test import grade_from_image  # 後で実装

app = Flask(__name__)

# ========= 環境変数 =========
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# ========= ヘルスチェック =========
@app.route("/", methods=["GET"])
def health():
    return "OK", 200

# ========= Webhook =========
@app.route("/webhook", methods=["POST"])
def webhook():
    # 署名検証（本番では必須）
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    if LINE_CHANNEL_SECRET:
        # 簡易：とりあえず未検証でも通す（後で強化可）
        pass

    try:
        events = json.loads(body)["events"]
    except Exception:
        abort(400)

    for event in events:
        handle_event(event)

    return "OK", 200


# ========= イベント処理 =========
def handle_event(event):
    if event["type"] != "message":
        return

    reply_token = event["replyToken"]
    user_id = event["source"]["userId"]

    message = event["message"]

    # --- テキスト ---
    if message["type"] == "text":
        text = message["text"]

        if text == "テスト":
            send_test(user_id)
            reply_message(reply_token, "問題を送信しました")
            return

        reply_message(reply_token, "「テスト」と送ると問題を出します")
        return

    # --- 画像（採点） ---
    if message["type"] == "image":
        message_id = message["id"]

        # TODO: 画像取得 → OCR → 採点
        result_text = grade_from_image(message_id)

        reply_message(reply_token, result_text)
        return


# ========= 出題 =========
def send_test(user_id):
    words = get_words()  # Sheetsから取得
    questions = generate_test(words, n=10)
    text = format_test(questions)

    push_message(user_id, text)


# ========= ローカル実行 =========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
import traceback

from fastapi import FastAPI, Request

from services.line_service import download_line_image, reply_message
from usecases.grade_submission import grade_submission


app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/callback")
async def callback(request: Request):
    body = await request.json()

    events = body.get("events", [])

    for event in events:
        reply_token = event.get("replyToken")
        message = event.get("message", {})
        message_type = message.get("type")

        if not reply_token:
            continue

        if message_type != "image":
            reply_message(
                reply_token=reply_token,
                text="答案画像を送ってください。",
            )
            continue

        message_id = message.get("id")

        if not message_id:
            reply_message(
                reply_token=reply_token,
                text="画像IDを取得できませんでした。",
            )
            continue

        try:
            image_path = download_line_image(
                message_id=message_id,
                save_path=f"/tmp/{message_id}.jpg",
            )

            result = grade_submission(image_path)

            reply_message(
                reply_token=reply_token,
                text=result["message"],
            )

        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e!r}", flush=True)
            traceback.print_exc()

            reply_message(
                reply_token=reply_token,
                text=(
                    "採点に失敗しました。\n"
                    "答案の上部に Test ID（例: #3）が書かれているか確認してください。"
                ),
            )

    return {"status": "ok"}

import os
import requests
from pathlib import Path

from services.settings import get_required_env


LINE_CHANNEL_ACCESS_TOKEN = get_required_env("LINE_CHANNEL_ACCESS_TOKEN")

def push_message(user_id, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(url, headers=headers, json=payload)

def reply_message(
    reply_token: str,
    text: str,
) -> None:
    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"LINE返信失敗: {response.status_code}\n{response.text}"
        )



def download_line_image(
    message_id: str,
    save_path: str,
) -> str:
    """
    LINEで送られた画像をダウンロードして保存する。
    """

    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"LINE画像取得失敗: {response.status_code}\n{response.text}"
        )

    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_bytes(response.content)

    return str(path)

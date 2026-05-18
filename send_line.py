import requests

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID
from generate_test import generate_test
from services.test_repository import save_test


PUSH_API_URL = "https://api.line.me/v2/bot/message/push"


def validate_settings() -> None:
    if not LINE_CHANNEL_ACCESS_TOKEN:
        raise ValueError("LINE_CHANNEL_ACCESS_TOKEN が未設定です。")

    if not LINE_USER_ID:
        raise ValueError("LINE_USER_ID が未設定です。")


def send_message(text: str) -> None:
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    response = requests.post(
        PUSH_API_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"送信失敗: {response.status_code}\n{response.text}"
        )

    print("送信成功")


def main() -> None:
    validate_settings()

    test_result = generate_test()
    test_text = test_result["test_text"]

    send_message(test_text)

    save_test(
        test_id=test_result["test_id"],
        indexes=test_result["indexes"],
    )

    print("送信したテスト:")
    print(test_result["test_id"])


if __name__ == "__main__":
    main()
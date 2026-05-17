import subprocess
import sys
from pathlib import Path

import requests

# ===== 設定 =====
CHANNEL_ACCESS_TOKEN = "LINEチャネルアクセストークン"
# USER_ID = "UserID"  # 
USER_ID = "UserID"  # 
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
GENERATE_TEST_SCRIPT = BASE_DIR / "generate_test.py"
# =================


def validate_settings() -> None:
    if "ここに" in CHANNEL_ACCESS_TOKEN or not CHANNEL_ACCESS_TOKEN.strip():
        raise ValueError("CHANNEL_ACCESS_TOKEN が未設定です。")

    if "ここに" in USER_ID or not USER_ID.strip():
        raise ValueError("USER_ID が未設定です。")


def generate_test_file() -> None:
    """generate_test.py を実行して、新しい単語テストを生成する。"""
    if not GENERATE_TEST_SCRIPT.exists():
        raise FileNotFoundError(f"生成スクリプトが見つかりません: {GENERATE_TEST_SCRIPT}")

    result = subprocess.run(
        [sys.executable, str(GENERATE_TEST_SCRIPT)],
        input="1\n",
        text=True,
        capture_output=True,
        check=False,
        cwd=str(BASE_DIR),
    )

    if result.returncode != 0:
        raise RuntimeError(
            "テスト生成に失敗しました。\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    print(result.stdout)


def get_latest_test_file() -> Path:
    """outputs 内の最新の *_test.txt を取得する。"""
    files = list(OUTPUT_DIR.glob("*_test.txt"))
    if not files:
        raise FileNotFoundError("outputs 内に *_test.txt が見つかりません。")

    return max(files, key=lambda path: path.stat().st_mtime)


def send_message(text: str) -> None:
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(
            f"送信失敗: {response.status_code}\n{response.text}"
        )

    print("送信成功")


def main():
    validate_settings()
    generate_test_file()
    latest_test_path = get_latest_test_file()
    text = latest_test_path.read_text(encoding="utf-8")
    send_message(text)
    print(f"送信したファイル: {latest_test_path}")


if __name__ == "__main__":
    main()

from PIL import Image

from services.ai_service import client


def extract_test_id_from_image(image_path: str) -> str:
    image = Image.open(image_path)

    prompt = """
画像は英単語テストの手書き答案です。

答案の上部に書かれている Test ID を読み取ってください。

# ルール
- Test ID は #数字 の形式です
- 例: #0, #1, #23
- 出力は Test ID のみ
- markdown禁止
- 説明禁止
- 読み取れない場合は UNKNOWN とだけ出力
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[prompt, image],
    )

    return response.text.strip()
from PIL import Image

from services.ai_service import client


def ocr_with_answers(
    image_path: str,
    questions: str,
    correct_answers: str,
) -> str:
    image = Image.open(image_path)

    prompt = f"""
あなたは英単語テスト答案のOCR補助AIです。

画像には、手書きの答案が写っています。
以下の問題一覧と模範解答を参考にして、生徒の回答をOCRしてください。

# 重要ルール
- 生徒の回答を勝手に正解へ修正しない
- ただし、明らかなOCR誤認と思われる文字は、問題文と模範解答を参考に補正してよい
- 読み取れない箇所は「不明」と書く
- 出力はプレーンテキストのみ
- markdown禁止
- 説明禁止

# 問題一覧
{questions}

# 模範解答
{correct_answers}

# 出力形式
test_id: #数字

1 生徒回答
2 生徒回答
...
20 生徒回答
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[prompt, image],
    )

    return response.text
from google import genai
from config import GEMINI_API_KEY

# Geminiクライアント作成
client = genai.Client(
	api_key=GEMINI_API_KEY
)

def ask_gemini(prompt: str) -> str:
	"""
	Geminiへ質問する
	"""

	response = client.models.generate_content(
		model = "gemini-2.5-flash-lite",
		contents=prompt
	)
	return response.text

from PIL import Image

def read_answers_from_image(image_path: str) -> str:
	"""
	答案画像をOCRする
	"""

	image = Image.open(image_path)
	prompt = """
画像は英単語テストの答案です．
画像の一番上にtest_idがあります．
左側に問題番号と日本語訳の問題の解答があります．
右側に問題番号と英語訳の問題の解答があります．

以下をOCRしてください．
- test_id
- 問題番号
- 生徒解答

出力はプレーンテキストのみ．
markdown禁止．
説明禁止．
"""

	response = client.models.generate_content(
		model = "gemini-2.5-flash-lite",
		contents=[
		prompt,
		image
	]
	)
	return response.text

import json
from services.ai_service import ask_gemini

def grade_answers():
	test_id = "#3"
	answer_text = """
1 create
2 increase
3 improve
4 mean
5 own
"""

	student_text = """
#3
1 create
2 increase
3 improve
4 mean
5 ownership
"""

	prompt = f"""
あなたは英単語テスト採点AIです．
# 絶対ルール

- JSONのみ返答
- markdown禁止
- 説明禁止
- 必ず valid JSON を返す
- 余計な文章を書かない
- wrong_numbersは整数配列
- score, total は整数

# test_id
{test_id}
# 模範解答
{answer_text}
# 生徒解答
{student_text}
# 採点ルール
- スペルミスは不正解
- 類義語は不正解
- 日本語訳は意味が一致すれば正解

# 出力形式
{{
	"score": 0
	"total": 0,
	"wrong_numbers": [],
	"wrong_words": [
		{{
			"index": 0,
			"number": 0,
			"word": "",
			"direction": "",
			"correct_answer": "",
			"student_answer": "",
			"reason": ""
		}}
	]
}}
"""
	response = ask_gemini(prompt)
	print("==== Gemini Raw Response =====")
	print(response)

	cleaned_response = response.replace("```json","")
	cleaned_response = cleaned_response.replace("```","")
	cleaned_response = cleaned_response.strip()
	print(cleaned_response)

	result = json.loads(cleaned_response)

	print("\n==== Parsed JSON =====")
	print(result)

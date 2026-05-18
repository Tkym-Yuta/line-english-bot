import json

from services.ai_service import ask_gemini
from services.ocr_with_answers import ocr_with_answers
from services.json_validator import validate_grading_result

MAX_RETRY = 2
TOTAL_QUESTIONS = 20


def clean_json_response(response: str) -> str:
    cleaned = response.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    return cleaned.strip()


def grade_from_image(image_path: str, questions: str, correct_answers: str) -> dict:
    # 1. 画像OCR
    ocr_text = ocr_with_answers(
        image_path=image_path,
        questions=questions,
        correct_answers=correct_answers,
    )

    print(
        f"[grade_from_ocr] OCR completed: {len(ocr_text)} chars",
        flush=True,
    )

    prompt = f"""
あなたは英単語テストの採点AIです。

# 絶対ルール
- JSONのみ返答
- markdown禁止
- 説明禁止
- 必ず valid JSON を返す
- 余計なキーを追加しない
- score は出力しない
- total は出力しない
- wrong_numbers のみ出力する
- wrong_numbers は間違えた問題番号の整数配列
- 間違いがない場合は wrong_numbers を [] にする
- 出力JSONのキーは wrong_numbers のみ

# 採点ルール
- 英語→日本語は、意味が十分一致していれば正解
- 日本語→英語は、指定された英単語と一致していれば正解
- スペルミスは不正解
- 類義語は原則不正解
- OCRの軽微な誤認は、文脈と模範解答から判断してよい
- 採点は「生徒のOCR結果」と「模範解答」で行う

# 生徒のOCR結果
{ocr_text}

# 模範解答
{correct_answers}

# 出力形式
{{
    "wrong_numbers": []
}}
"""

    for attempt in range(MAX_RETRY + 1):
        response = ask_gemini(prompt)

        print(
            f"[grade_from_ocr] grading attempt {attempt + 1}",
            flush=True,
        )

        cleaned = clean_json_response(response)

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse failed: {e}", flush=True)
            continue

        if validate_grading_result(result):
            wrong_numbers = result["wrong_numbers"]
            result["total"] = TOTAL_QUESTIONS
            result["score"] = TOTAL_QUESTIONS - len(wrong_numbers)

            print(
                "[grade_from_ocr] grading completed: "
                f"score={result['score']}/{result['total']}, "
                f"wrong_count={len(wrong_numbers)}",
                flush=True,
            )

            return result

        print("[ERROR] Invalid grading result. Retrying...", flush=True)

    raise RuntimeError("Gemini採点JSONの検証に失敗しました。")

from services.test_id_ocr import extract_test_id_from_image
from services.test_repository import get_indexes_by_test_id
from services.test_builder import build_test_data
from services.submission_repository import save_submission
from services.wrong_word_repository import save_wrong_words
from usecases.grade_from_ocr import grade_from_image
from usecases.format_result import format_grading_result


def grade_submission(image_path: str) -> dict:
    # 1. 画像から test_id をOCR
    test_id = extract_test_id_from_image(image_path)

    if test_id == "UNKNOWN":
        raise RuntimeError("test_id を読み取れませんでした。")

    # 2. test_id から indexes を取得
    indexes = get_indexes_by_test_id(test_id)

    # 3. indexes から questions / correct_answers / test_metadata を生成
    test_data = build_test_data(indexes)

    # 4. 採点
    result = grade_from_image(
        image_path=image_path,
        questions=test_data["questions"],
        correct_answers=test_data["correct_answers"],
    )
    
    # 5. 採点結果をDBに保存
    save_submission(
        test_id=test_id,
        result=result,
    )
    
    # 6. 間違えた問題をDBに保存
    save_wrong_words(
        test_id=test_id,
        result=result,
        test_metadata=test_data["test_metadata"],
    )

    # 7. LINE返信用メッセージ生成
    message = format_grading_result(
        result=result,
        test_metadata=test_data["test_metadata"],
    )

    return {
        "test_id": test_id,
        "indexes": indexes,
        "result": result,
        "message": message,
    }
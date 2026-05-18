from datetime import datetime

from services.sheets_service import append_row


SUBMISSIONS_SHEET_NAME = "Submissions"


def save_submission(
    test_id: str,
    result: dict,
) -> None:
    score = result["score"]
    total = result["total"]
    wrong_numbers = result["wrong_numbers"]

    wrong_numbers_text = ",".join(map(str, wrong_numbers))

    append_row(
        SUBMISSIONS_SHEET_NAME,
        [
            datetime.now().isoformat(),
            test_id,
            score,
            total,
            wrong_numbers_text,
        ],
    )
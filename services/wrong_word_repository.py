from datetime import datetime

from services.sheets_service import get_worksheet


WRONG_WORDS_SHEET_NAME = "WrongWords"


def get_wrong_word_indexes() -> list[int]:
    worksheet = get_worksheet(WRONG_WORDS_SHEET_NAME)
    records = worksheet.get_all_records()

    indexes = []

    for row in records:
        if not row.get("index"):
            continue

        indexes.append(int(row["index"]))

    return indexes


def save_wrong_words(
    test_id: str,
    result: dict,
    test_metadata: dict,
) -> None:
    worksheet = get_worksheet(WRONG_WORDS_SHEET_NAME)
    records = worksheet.get_all_records()

    row_number_by_index = {}

    for i, row in enumerate(records, start=2):
        if not row.get("index"):
            continue

        row_number_by_index[int(row["index"])] = i

    now = datetime.now().isoformat()
    wrong_numbers = result["wrong_numbers"]

    for problem_number in wrong_numbers:
        info = test_metadata.get(problem_number)

        if info is None:
            continue

        target_index = int(info["index"])
        target_number = int(info["number"])
        word = info["word"]
        direction = info["direction"]

        if target_index in row_number_by_index:
            row_number = row_number_by_index[target_index]

            current_count = worksheet.cell(row_number, 5).value
            current_count = int(current_count) if current_count else 0

            worksheet.update_cell(row_number, 5, current_count + 1)
            worksheet.update_cell(row_number, 6, now)

        else:
            worksheet.append_row([
                target_index,
                target_number,
                word,
                direction,
                1,
                now,
            ])

def get_wrong_word_records() -> list[dict]:
    worksheet = get_worksheet(WRONG_WORDS_SHEET_NAME)
    records = worksheet.get_all_records()

    wrong_words = []

    for row in records:
        if not row.get("index"):
            continue

        wrong_words.append({
            "index": int(row["index"]),
            "miss_count": int(row.get("miss_count", 1)),
        })

    return wrong_words
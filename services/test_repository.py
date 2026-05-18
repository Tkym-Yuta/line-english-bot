from datetime import datetime

from services.sheets_service import get_worksheet


TESTS_SHEET_NAME = "Tests"


def parse_indexes(indexes_text: str) -> list[int]:
    indexes_text = indexes_text.replace("'", "")
    return [
        int(x.strip())
        for x in indexes_text.split(",")
        if x.strip()
    ]


def save_test(
    test_id: str,
    indexes: list[int],
) -> None:

    worksheet = get_worksheet(TESTS_SHEET_NAME)

    indexes_text = "'" + ",".join(map(str, indexes))

    worksheet.append_row([
        test_id,
        datetime.now().isoformat(),
        indexes_text,
    ])


def get_indexes_by_test_id(
    test_id: str,
) -> list[int]:

    worksheet = get_worksheet(TESTS_SHEET_NAME)

    records = worksheet.get_all_records()

    for row in records:

        row_test_id = str(
            row["test_id"]
        ).strip()

        if row_test_id == test_id.strip():

            return parse_indexes(
                str(row["indexes"])
            )

    raise ValueError(
        f"test_id={test_id} が "
        f"Tests シートに見つかりません。"
    )
    
def get_next_test_id() -> str:
    worksheet = get_worksheet(TESTS_SHEET_NAME)

    records = worksheet.get_all_records()

    return f"#{len(records)}"
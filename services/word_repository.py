import csv


TARGET_CSV_PATH = "TARGET1900.csv"


def load_words() -> dict:
    """
    TARGET1900.csv を読み込み、
    index をキーにした辞書を返す。
    """

    words = {}

    with open(TARGET_CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            index = int(row["index"])

            words[index] = {
                "index": index,
                "number": int(row["number"]),
                "word": row["word"],
                "meaning": row["meaning"],
                "type": row["type"],
            }

    return words


def get_words_by_indexes(indexes: list[int]) -> list[dict]:
    """
    指定された index の単語情報を取得する。
    """

    words = load_words()

    selected_words = []

    for index in indexes:
        if index not in words:
            raise ValueError(f"TARGET1900.csv に index={index} が存在しません。")

        selected_words.append(words[index])

    return selected_words
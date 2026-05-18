from services.word_repository import get_words_by_indexes


QUESTION_COUNT = 20
EN_TO_JA_COUNT = 10
JA_TO_EN_COUNT = 10


def build_questions(words: list[dict]) -> str:
    lines = []

    for i, word_data in enumerate(words, start=1):
        if i <= EN_TO_JA_COUNT:
            question = word_data["word"]
        else:
            question = word_data["meaning"]

        lines.append(f"{i} {question}")

    return "\n".join(lines)


def build_correct_answers(words: list[dict]) -> str:
    lines = []

    for i, word_data in enumerate(words, start=1):
        if i <= EN_TO_JA_COUNT:
            answer = word_data["meaning"]
        else:
            answer = word_data["word"]

        lines.append(f"{i} {answer}")

    return "\n".join(lines)


def build_test_metadata(words: list[dict]) -> dict:
    metadata = {}

    for i, word_data in enumerate(words, start=1):
        if i <= EN_TO_JA_COUNT:
            direction = "en_to_ja"
        else:
            direction = "ja_to_en"

        metadata[i] = {
            "index": word_data["index"],
            "number": word_data["number"],
            "word": word_data["word"],
            "direction": direction,
        }

    return metadata


def build_test_data(indexes: list[int]) -> dict:
    if len(indexes) != QUESTION_COUNT:
        raise ValueError(
            f"問題数が不正です: {len(indexes)}問 "
            f"(expected: {QUESTION_COUNT})"
        )

    words = get_words_by_indexes(indexes)

    return {
        "questions": build_questions(words),
        "correct_answers": build_correct_answers(words),
        "test_metadata": build_test_metadata(words),
    }
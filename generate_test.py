import csv
import random
from datetime import datetime
from pathlib import Path
from services.test_repository import get_next_test_id
from services.wrong_word_repository import get_wrong_word_records

# ===== 基本設定 =====
CSV_PATH = "TARGET1900.csv"
OUTPUT_DIR = Path("outputs")

RANGES_CONFIG = [
    {"start": 1001, "end": 1100, "count": 10},
    {"start": 1101, "end": 1200, "count": 10},
]

NUM_EN_TO_JP = 10
TOTAL_QUESTIONS = 20
SEED = None
REVIEW_COUNT = 4
# ==================


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)


def load_words(csv_path: str) -> list[dict]:
    words = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row["index"] = int(row["index"])
            row["number"] = int(row["number"])
            words.append(row)

    return words


def get_candidates(words: list[dict], start: int, end: int) -> list[dict]:
    return [
        word for word in words
        if start <= word["number"] <= end
    ]


def sample_from_ranges(
    words: list[dict],
    ranges_config: list[dict],
    rng: random.Random,
) -> list[dict]:
    selected = []
    used_indexes = set()

    for config in ranges_config:
        candidates = [
            word for word in get_candidates(
                words,
                config["start"],
                config["end"],
            )
            if word["index"] not in used_indexes
        ]

        count = config["count"]

        if len(candidates) < count:
            raise ValueError(
                f"範囲 {config['start']}〜{config['end']} に単語が足りません。"
                f"必要: {count}問 / 利用可能: {len(candidates)}問"
            )

        sampled = rng.sample(candidates, count)
        selected.extend(sampled)

        for word in sampled:
            used_indexes.add(word["index"])

    return selected


def adjust_ranges_config(ranges_config: list[dict], total_count: int) -> list[dict]:
    total_base_count = sum(config["count"] for config in ranges_config)

    if total_base_count <= 0:
        raise ValueError("RANGES_CONFIG の count 合計は1以上にしてください。")

    adjusted = []
    allocated_count = 0

    for i, config in enumerate(ranges_config):
        if i == len(ranges_config) - 1:
            count = total_count - allocated_count
        else:
            count = total_count * config["count"] // total_base_count
            allocated_count += count

        adjusted.append({
            "start": config["start"],
            "end": config["end"],
            "count": count,
        })

    return adjusted


def split_questions(selected: list[dict]) -> tuple[list[dict], list[dict]]:
    if len(selected) != TOTAL_QUESTIONS:
        raise ValueError(
            f"出題数が不正です: {len(selected)}問 "
            f"(expected: {TOTAL_QUESTIONS})"
        )

    en_to_jp = selected[:NUM_EN_TO_JP]
    jp_to_en = selected[NUM_EN_TO_JP:]

    return jp_to_en, en_to_jp


def build_test_text(
    test_id: str,
    jp_to_en: list[dict],
    en_to_jp: list[dict],
) -> str:
    lines = []

    lines.append("単語テスト")
    lines.append(f"Test ID: {test_id}")
    lines.append("※答案の一番上にこのIDを書いてください。")
    lines.append("")

    lines.append("【A】日本語訳（英語→日本語）")
    for i, word in enumerate(en_to_jp, start=1):
        lines.append(f"{i}. {word['word']}")

    lines.append("")
    lines.append("【B】英訳（日本語→英語）")
    for i, word in enumerate(jp_to_en, start=NUM_EN_TO_JP + 1):
        lines.append(f"{i}. {word['meaning']}")

    return "\n".join(lines)


def build_answer_text(
    jp_to_en: list[dict],
    en_to_jp: list[dict],
) -> str:
    lines = []

    lines.append("解答")
    lines.append("")

    lines.append("【A】")
    for i, word in enumerate(en_to_jp, start=1):
        lines.append(
            f"{i}. [{word['number']}番] "
            f"{word['word']} = {word['meaning']}"
        )

    lines.append("")
    lines.append("【B】")
    for i, word in enumerate(jp_to_en, start=NUM_EN_TO_JP + 1):
        lines.append(
            f"{i}. [{word['number']}番] "
            f"{word['meaning']} = {word['word']}"
        )

    return "\n".join(lines)


def build_ordered_indexes(
    jp_to_en: list[dict],
    en_to_jp: list[dict],
) -> list[int]:
    ordered_words = en_to_jp + jp_to_en
    return [word["index"] for word in ordered_words]


def save_debug_files(
    test_id: str,
    test_text: str,
    answer_text: str,
    indexes: list[int],
) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_test_id = test_id.replace("#", "")

    test_path = OUTPUT_DIR / f"test_{safe_test_id}_{timestamp}_test.txt"
    answer_path = OUTPUT_DIR / f"test_{safe_test_id}_{timestamp}_answer.txt"
    indexes_path = OUTPUT_DIR / f"test_{safe_test_id}_{timestamp}_indexes.txt"

    test_path.write_text(test_text, encoding="utf-8")
    answer_path.write_text(answer_text, encoding="utf-8")
    indexes_path.write_text(
        ",".join(map(str, indexes)),
        encoding="utf-8",
    )

    print("保存先:")
    print(test_path)
    print(answer_path)
    print(indexes_path)

def get_words_by_indexes(words: list[dict], indexes: list[int]) -> list[dict]:
    word_by_index = {
        word["index"]: word
        for word in words
    }

    selected = []

    for index in indexes:
        if index in word_by_index:
            selected.append(word_by_index[index])

    return selected

def sample_review_words_by_weight(
    words: list[dict],
    wrong_records: list[dict],
    review_count: int,
    rng: random.Random,
) -> list[dict]:
    if review_count <= 0 or not wrong_records:
        return []

    word_by_index = {
        word["index"]: word
        for word in words
    }

    candidates = []

    for record in wrong_records:
        index = record["index"]
        miss_count = record["miss_count"]

        if index not in word_by_index:
            continue

        candidates.append({
            "word_data": word_by_index[index],
            "weight": max(1, miss_count),
        })

    selected = []

    while candidates and len(selected) < review_count:
        total_weight = sum(item["weight"] for item in candidates)
        r = rng.uniform(0, total_weight)

        current = 0

        for i, item in enumerate(candidates):
            current += item["weight"]

            if r <= current:
                selected.append(item["word_data"])
                candidates.pop(i)
                break

    return selected

def generate_test() -> dict:
    ensure_output_dir()

    rng = random.Random(SEED)
    words = load_words(CSV_PATH)

    wrong_records = get_wrong_word_records()

    review_words = sample_review_words_by_weight(
        words=words,
        wrong_records=wrong_records,
        review_count=REVIEW_COUNT,
        rng=rng,
    )
    excluded_indexes = {
        word["index"]
        for word in review_words
    }

    new_question_count = TOTAL_QUESTIONS - len(review_words)

    adjusted_ranges_config = adjust_ranges_config(
        ranges_config=RANGES_CONFIG,
        total_count=new_question_count,
    )

    new_words = sample_from_ranges(
        words=[
            word for word in words
            if word["index"] not in excluded_indexes
        ],
        ranges_config=adjusted_ranges_config,
        rng=rng,
    )

    selected = review_words + new_words

    rng.shuffle(selected)

    jp_to_en, en_to_jp = split_questions(selected)

    test_id = get_next_test_id()

    test_text = build_test_text(
        test_id=test_id,
        jp_to_en=jp_to_en,
        en_to_jp=en_to_jp,
    )

    answer_text = build_answer_text(
        jp_to_en=jp_to_en,
        en_to_jp=en_to_jp,
    )

    indexes = build_ordered_indexes(
        jp_to_en=jp_to_en,
        en_to_jp=en_to_jp,
    )
    
    
    save_debug_files(
        test_id=test_id,
        test_text=test_text,
        answer_text=answer_text,
        indexes=indexes,
    )

    return {
        "test_id": test_id,
        "test_text": test_text,
        "answer_text": answer_text,
        "indexes": indexes,
    }


if __name__ == "__main__":
    result = generate_test()

    print()
    print(result["test_text"])

    print()
    print("=" * 40)
    print()

    print(result["answer_text"])

    print()
    print("indexes:")
    print(result["indexes"])

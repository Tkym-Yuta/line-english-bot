

import csv
import random
from datetime import datetime
from pathlib import Path


CSV_COLUMNS = ["index", "number", "word", "meaning", "type"]
LAST_TEST_COLUMNS = ["question_no", "direction", "index", "number", "word", "meaning", "type"]


# ===== 基本設定 =====
CSV_PATH = "TARGET1900.csv"
WRONG_WORDS_PATH = "wrong_words.csv"
OUTPUT_DIR = Path("outputs")
TEST_NAME = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# 新規問題の範囲指定（必要に応じて変更）
RANGES_CONFIG = [
    {"start": 801, "end": 900, "count": 8},
    {"start": 901, "end": 1000, "count": 8},
]

REVIEW_COUNT = 4  # wrong_words.csv から復習として出す問題数
NUM_EN_TO_JP = 10  # 英語→日本語
TOTAL_QUESTIONS = 20
SEED = None
# ==================


def ensure_output_dir():
    OUTPUT_DIR.mkdir(exist_ok=True)


def load_words(csv_path):
    words = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["index"] = int(row["index"])
            row["number"] = int(row["number"])
            words.append(row)
    return words


def ensure_csv_file(path, columns):
    file_path = Path(path)
    if file_path.exists():
        return
    with file_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()


def load_wrong_words(path):
    ensure_csv_file(path, CSV_COLUMNS)
    words = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("index"):
                continue
            row["index"] = int(row["index"])
            row["number"] = int(row["number"])
            words.append(row)
    return words


def save_wrong_words(path, words):
    unique = {}
    for word in words:
        unique[int(word["index"])] = {
            "index": int(word["index"]),
            "number": int(word["number"]),
            "word": word["word"],
            "meaning": word["meaning"],
            "type": word["type"],
        }

    sorted_words = sorted(unique.values(), key=lambda x: x["index"])

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(sorted_words)


def get_candidates(words, start, end):
    return [w for w in words if start <= w["number"] <= end]


def sample_review_words(wrong_words, review_count, rng):
    if review_count <= 0 or not wrong_words:
        return []
    count = min(review_count, len(wrong_words))
    return rng.sample(wrong_words, count)


def sample_from_ranges(words, ranges_config, excluded_indices, rng):
    selected = []

    for r in ranges_config:
        candidates = [
            w for w in get_candidates(words, r["start"], r["end"])
            if w["index"] not in excluded_indices
        ]
        if len(candidates) < r["count"]:
            raise ValueError(
                f"範囲 {r['start']}〜{r['end']} に単語が足りません（必要 {r['count']} 問、利用可能 {len(candidates)} 問）"
            )

        sampled = rng.sample(candidates, r["count"])
        selected.extend(sampled)
        excluded_indices.update(w["index"] for w in sampled)

    return selected


def split_questions(selected, num_en_to_jp):
    if num_en_to_jp > len(selected):
        raise ValueError("英語→日本語の問題数が合計問題数を超えています")
    en_to_jp = selected[:num_en_to_jp]
    jp_to_en = selected[num_en_to_jp:]
    return jp_to_en, en_to_jp


def build_test(jp_to_en, en_to_jp):
    lines = []
    lines.append("単語テスト\n")

    lines.append("【A】日本語訳（英語→日本語）\n")
    for i, w in enumerate(en_to_jp, 1):
        lines.append(f"{i}. {w['word']} ({w['number']}番)")

    lines.append("\n【B】英訳（日本語→英語）\n")
    for i, w in enumerate(jp_to_en, len(en_to_jp) + 1):
        lines.append(f"{i}. {w['meaning']} ({w['number']}番)")

    return "\n".join(lines)


def build_answer(jp_to_en, en_to_jp):
    lines = []
    lines.append("解答\n")

    lines.append("【A】\n")
    for i, w in enumerate(en_to_jp, 1):
        lines.append(f"{i}. [{w['number']}番] {w['word']} = {w['meaning']}")

    lines.append("\n【B】\n")
    for i, w in enumerate(jp_to_en, len(en_to_jp) + 1):
        lines.append(f"{i}. [{w['number']}番] {w['meaning']} = {w['word']}")

    return "\n".join(lines)


def save_last_test_questions(path, jp_to_en, en_to_jp):
    rows = []

    for i, w in enumerate(en_to_jp, 1):
        rows.append({
            "question_no": i,
            "direction": "en_to_jp",
            "index": w["index"],
            "number": w["number"],
            "word": w["word"],
            "meaning": w["meaning"],
            "type": w["type"],
        })

    start_no = len(en_to_jp) + 1
    for i, w in enumerate(jp_to_en, start_no):
        rows.append({
            "question_no": i,
            "direction": "jp_to_en",
            "index": w["index"],
            "number": w["number"],
            "word": w["word"],
            "meaning": w["meaning"],
            "type": w["type"],
        })

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LAST_TEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def load_last_test_questions(path):
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"前回問題ファイルが見つかりません: {path}")

    rows = []
    with file_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["question_no"] = int(row["question_no"])
            row["index"] = int(row["index"])
            row["number"] = int(row["number"])
            rows.append(row)
    return rows


def parse_question_numbers(text):
    if not text.strip():
        return []
    numbers = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        numbers.append(int(part))
    return numbers


def update_wrong_words_from_last_test(last_test_path, wrong_words_path):
    last_test_rows = load_last_test_questions(last_test_path)
    wrong_words = load_wrong_words(wrong_words_path)

    print(f"採点対象: {last_test_path}")
    user_input = input("間違えた問題番号をカンマ区切りで入力してください（例: 2,5,13）。全部正解なら Enter: ").strip()
    wrong_question_nos = set(parse_question_numbers(user_input))

    row_by_qno = {row["question_no"]: row for row in last_test_rows}

    invalid = [q for q in wrong_question_nos if q not in row_by_qno]
    if invalid:
        raise ValueError(f"存在しない問題番号があります: {invalid}")

    current_wrong_by_index = {w["index"]: w for w in wrong_words}

    for row in last_test_rows:
        index = row["index"]
        if row["question_no"] in wrong_question_nos:
            current_wrong_by_index[index] = {
                "index": row["index"],
                "number": row["number"],
                "word": row["word"],
                "meaning": row["meaning"],
                "type": row["type"],
            }
        else:
            current_wrong_by_index.pop(index, None)

    save_wrong_words(wrong_words_path, list(current_wrong_by_index.values()))
    print(f"wrong_words.csv を更新しました。現在の復習対象数: {len(current_wrong_by_index)}")


def generate_test():
    ensure_output_dir()
    ensure_csv_file(WRONG_WORDS_PATH, CSV_COLUMNS)

    rng = random.Random(SEED)
    words = load_words(CSV_PATH)
    wrong_words = load_wrong_words(WRONG_WORDS_PATH)

    review_words = sample_review_words(wrong_words, REVIEW_COUNT, rng)
    excluded_indices = {w["index"] for w in review_words}

    remaining_slots = TOTAL_QUESTIONS - len(review_words)
    if remaining_slots < 0:
        remaining_slots = 0

    adjusted_ranges_config = []
    base_total = sum(r["count"] for r in RANGES_CONFIG)
    if base_total <= 0 and remaining_slots > 0:
        raise ValueError("RANGES_CONFIG の count の合計が 0 です")

    allocated = 0
    for i, r in enumerate(RANGES_CONFIG):
        if i == len(RANGES_CONFIG) - 1:
            count = remaining_slots - allocated
        else:
            count = remaining_slots * r["count"] // base_total
            allocated += count

        adjusted_ranges_config.append({
            "start": r["start"],
            "end": r["end"],
            "count": count,
        })

    new_words = sample_from_ranges(words, adjusted_ranges_config, excluded_indices, rng)

    selected = review_words + new_words
    rng.shuffle(selected)

    total_questions = len(selected)
    if total_questions == 0:
        raise ValueError("出題できる単語がありません")
    if total_questions != TOTAL_QUESTIONS:
        raise ValueError(f"出題数が {TOTAL_QUESTIONS} 問になっていません（実際: {total_questions} 問）")
    if NUM_EN_TO_JP > total_questions:
        raise ValueError("英語→日本語の問題数が出題総数を超えています")

    jp_to_en, en_to_jp = split_questions(selected, NUM_EN_TO_JP)

    test = build_test(jp_to_en, en_to_jp)
    answer = build_answer(jp_to_en, en_to_jp)

    print(test)
    print("\n" + "=" * 40 + "\n")
    print(answer)

    test_path = OUTPUT_DIR / f"{TEST_NAME}_test.txt"
    answer_path = OUTPUT_DIR / f"{TEST_NAME}_answer.txt"
    last_test_path = OUTPUT_DIR / f"{TEST_NAME}_questions.csv"

    test_path.write_text(test, encoding="utf-8")
    answer_path.write_text(answer, encoding="utf-8")
    save_last_test_questions(last_test_path, jp_to_en, en_to_jp)

    print("\n保存先:")
    print(test_path)
    print(answer_path)
    print(last_test_path)

    print("\n今回の復習出題数:", len(review_words))
    print("今回の新規出題数:", len(new_words))
    print("今回の合計出題数:", len(selected))


def main():
    print("モードを選んでください:")
    print("1: テスト生成")
    print("2: 採点結果を反映して wrong_words.csv を更新")
    mode = input("番号を入力: ").strip()

    if mode == "1":
        generate_test()
    elif mode == "2":
        question_files = list(OUTPUT_DIR.glob("*_questions.csv"))
        if not question_files:
            raise FileNotFoundError("outputs 内に *_questions.csv が見つかりません")
        default_path = max(question_files, key=lambda path: path.stat().st_mtime)
        path_input = input(
            f"採点対象の questions.csv を入力してください（Enterで {default_path}）: "
        ).strip()
        target_path = path_input if path_input else str(default_path)
        update_wrong_words_from_last_test(target_path, WRONG_WORDS_PATH)
    else:
        print("1 か 2 を入力してください。")


if __name__ == "__main__":
    main()
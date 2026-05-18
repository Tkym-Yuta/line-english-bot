def format_grading_result(result: dict, test_metadata: dict) -> str:
    score = result.get("score", 0)
    total = result.get("total", 0)
    wrong_numbers = result.get("wrong_numbers", [])

    lines = []

    lines.append(f"採点結果 : {score}/{total}")
    lines.append("")

    if not wrong_numbers:
        lines.append("全問正解！")
        return "\n".join(lines)

    lines.append("間違い:")
    lines.append("")

    for problem_number in wrong_numbers:
        info = test_metadata.get(problem_number)

        if info is None:
            lines.append(f"{problem_number} 不明(不明)")
            continue

        word = info["word"]
        target_number = info["number"]

        lines.append(
            f"{problem_number} {word}({target_number})"
        )

    return "\n".join(lines)
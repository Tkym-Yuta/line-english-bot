def validate_grading_result(result: dict) -> bool:
    """
    採点JSONを検証する。
    仕様:
    {
        "wrong_numbers": list[int]
    }
    """

    required_keys = [
        "wrong_numbers",
    ]

    for key in required_keys:
        if key not in result:
            print(f"[ERROR] Missing key: {key}")
            return False


    if not isinstance(result["wrong_numbers"], list):
        print("[ERROR] wrong_numbers is not list")
        return False

    for number in result["wrong_numbers"]:
        if not isinstance(number, int):
            print("[ERROR] wrong_numbers contains non-int value")
            return False

        if number < 1 or number > 20:
            print(f"[ERROR] wrong number out of range: {number}")
            return False

    
    return True
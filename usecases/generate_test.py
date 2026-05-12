import random

def generate_test(words, n=10):
    return random.sample(words, n)

def format_test(questions):
    text = "【英単語テスト】\n"
    for q in questions:
        text += f"{q['number']}. {q['meaning']}\n"
    return text
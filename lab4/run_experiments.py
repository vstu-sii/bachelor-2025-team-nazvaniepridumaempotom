import json
import time
from pathlib import Path
import pandas as pd

from src.model_wrapper import llama_generate
from src.token_utils import count_tokens

TEST_PATH = Path("data/test_cases.jsonl")
RESULTS_PATH = Path("data/eval_results.jsonl")


def load_test_cases(path: Path):
    tests = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            tests.append(json.loads(line))
    return tests


def run_test(description: str):
    system_prompt = "Ты — эксперт по еде. Проанализируй описание блюда и оцени его. Дай оценку от 1 до 10 и коротко объясни почему."
    user_prompt = description

    start = time.time()
    response = llama_generate(system=system_prompt, user=user_prompt)
    latency = round(time.time() - start, 3)

    input_tokens = count_tokens(system_prompt + " " + user_prompt)
    output_tokens = count_tokens(response)

    return {
        "description": description,
        "response": response,
        "latency_sec": latency,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens
    }


def main():
    tests = load_test_cases(TEST_PATH)

    results = []
    for i, test in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] {test['description']}")
        res = run_test(test["description"])
        results.append(res)

    # сохраняем в JSONL
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("Сохранено:", RESULTS_PATH)

    # базовый анализ
    df = pd.DataFrame(results)

    print("\n--- Статистика ---")
    print("Средний latency:", df["latency_sec"].mean())
    print("Среднее input tokens:", df["input_tokens"].mean())
    print("Среднее output tokens:", df["output_tokens"].mean())
    print("Среднее total tokens:", df["total_tokens"].mean())

    print("\n--- Самые долгие ответы ---")
    print(df.sort_values("latency_sec", ascending=False).head(3)[["description", "latency_sec", "output_tokens"]])


if __name__ == "__main__":
    main()

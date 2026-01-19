import requests
import json
from time import sleep
from random import randint

API_URL = "http://127.0.0.1:8000/evaluate/text/metrics"
OUTPUT_FILE = "data/ab_test_results.jsonl"

TEST_CASES = [
    "Салат Цезарь с курицей, листовой салат, сухарики, соус цезарь.",
    "Борщ украинский с говядиной, сметаной и чесноком.",
    "Паста карбонара с беконом и пармезаном.",
    "Омлет с сыром и зеленью, подается с тостами.",
    "Рис с овощами и курицей в соевом соусе.",
    "Суши ролл с лососем и авокадо.",
    "Том ям с креветками и кокосовым молоком.",
    "Куриные крылышки в медово-горчичном соусе.",
    "Печеная картошка с розмарином и чесноком.",
    "Чизкейк с клубничным соусом."
]

def main():
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for i in range(len(TEST_CASES)):
            data = {"description": TEST_CASES[i]}
            resp = requests.post(API_URL, json=data)

            if resp.status_code != 200:
                print(f"Ошибка: {resp.status_code} | {resp.text}")
                continue

            result = resp.json()
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

            print(f"[{i+1}/{len(TEST_CASES)}] saved: variant={result['variant']} tokens={result['total_tokens']}")

            sleep(0.5)  # чтобы не перегрузить сервер

if __name__ == "__main__":
    main()

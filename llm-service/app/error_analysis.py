import json

REPORT_PATH = "data/processed/eval_report.jsonl"
OUTPUT_PATH = "data/processed/error_report.jsonl"

def analyze_errors():
    results = []
    print("Читаю eval_report.jsonl...")

    with open(REPORT_PATH, "r") as f:
        for line in f:
            entry = json.loads(line)

            issues = []

            # --- 1. низкие метрики ---
            if entry["bleu"] < 0.05:
                issues.append("BLEU слишком низкий (почти нет совпадений)")

            if entry["rouge_l"] < 0.1:
                issues.append("ROUGE-L очень низкий → модель не повторяет ключевые элементы")

            # --- 2. модель слишком болтлива ---
            if entry["output_length"] > entry["input_length"] * 3:
                issues.append("Слишком длинный ответ → возможно галлюцинация")

            # --- 3. модель вообще не упоминает еду ---
            food_keywords = ["ингредиент", "блюдо", "рецепт", "готов", "кухн", "dish", "cook", "recipe"]
            if not any(word.lower() in entry["output_text"].lower() for word in food_keywords):
                issues.append("В ответе нет упоминаний еды → оффтоп")

            # --- 4. Чрезмерное повторение слов ---
            words = entry["output_text"].split()
            unique_ratio = len(set(words)) / max(1, len(words))
            if unique_ratio < 0.3:
                issues.append("Повторяемость текста → модель зацикливается")

            entry["issues"] = issues
            results.append(entry)

    # сохраняем отчёт
    with open(OUTPUT_PATH, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Готово. Отчёт: {OUTPUT_PATH}")


if __name__ == "__main__":
    analyze_errors()

import json
import time
from src.model_wrapper import llama_generate
from src.prompt_loader import load_prompt
from src.metrics import compute_bleu, compute_rouge


TEST_PATH = "data/processed/test.jsonl"
REPORT_PATH = "data/processed/eval_report.jsonl"


def evaluate_sample(sample):
    """
    Оценивает один пример из датасета.
    Формирует промпт, вызывает модель и собирает результат.
    """

    # --- 1. Собираем описание блюда ---
    description = ""

    if sample.get("cleaned_ingredients"):
        description += sample["cleaned_ingredients"] + "\n"

    if sample.get("instructions"):
        description += sample["instructions"]

    if not description.strip():
        description = "Нет данных для анализа."

    # --- 2. Загружаем SystemPrompt и UserPrompt ---
    system_prompt, user_prompt = load_prompt("src/prompts/food_evaluation_prompt.json")


    # Подставляем данные в user prompt
    final_user_prompt = user_prompt.format(description=description)

    # --- 3. отправляем в LLaMA ---
    start_time = time.time()
    response = llama_generate(
        system=system_prompt,
        user=final_user_prompt
    )
    latency = round(time.time() - start_time, 3)

    # --- 4. Метрики ---
    bleu = compute_bleu(description, response)
    rouge_scores = compute_rouge(description, response)


    return {
        "input_description": description,
        "latency_sec": latency,
        "output_text": response,
        "input_length": len(final_user_prompt),
        "output_length": len(response),

        # --- Метрики ---
        "bleu": bleu,
        "rouge_1": rouge_scores["rouge-1"],
        "rouge_2": rouge_scores["rouge-2"],
        "rouge_l": rouge_scores["rouge-l"],
    }


def run_evaluation(limit=10):
    """
    Прогоняет N примеров из тестового датасета.
    """

    print(f"Загружаю тестовый датасет: {TEST_PATH}")

    results = []
    count = 0

    with open(TEST_PATH, "r") as f:
        for line in f:
            if count >= limit:
                break

            sample = json.loads(line)
            count += 1

            print(f"[{count}/{limit}] Обрабатываю пример...")

            result = evaluate_sample(sample)
            results.append(result)

    print(f"Сохраняю отчёт: {REPORT_PATH}")
    with open(REPORT_PATH, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\nEvaluation завершён!")
    print(f"Всего примеров: {limit}")


if __name__ == "__main__":
    run_evaluation(limit=5)

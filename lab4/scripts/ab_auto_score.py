import csv
import re
from collections import defaultdict

INPUT_CSV = "data/ab_results_analysis.csv"
OUTPUT_CSV = "data/ab_results_scored.csv"

def score_response(text: str) -> int:
    """
    Простейшая авто-оценка:
    - 5: отличный ответ, без ошибок и по формату
    - 4: хороший, но есть мелкие ошибки
    - 3: нормальный, но заметны ошибки/неровности
    - 2: плохой (много ошибок, не по формату)
    - 1: почти не ответил
    - 0: вообще не по теме
    """
    t = text.lower()

    # если вообще пусто
    if not t.strip():
        return 0

    # проверка на английские вставки (снижаем оценку)
    eng_words = ["example", "protein", "salad", "dish", "flavor", "snack", "vitamin", "good", "bad", "however"]
    eng_count = sum(1 for w in eng_words if w in t)

    # проверка формата (для варианта B/C — где должен быть список/строго)
    has_score = bool(re.search(r"оценк[аи]:?\s*\d", t))
    has_expl = "объясн" in t or "обосн" in t
    has_list = "*" in t or "1)" in t or "2)" in t

    # базовая оценка
    score = 5

    if not has_score:
        score -= 2
    if not has_expl:
        score -= 1
    if eng_count >= 2:
        score -= 2
    if eng_count == 1:
        score -= 1
    if not has_list and "вариант" in t:
        score -= 1

    if score < 0:
        score = 0
    return score


# -----------------------------
# Читаем CSV, ставим score
# -----------------------------
rows = []
stats = defaultdict(lambda: {"count": 0, "score_sum": 0})

with open(INPUT_CSV, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        resp = row["response"]
        sc = score_response(resp)

        row["quality_score"] = sc
        rows.append(row)

        v = row["variant"]
        stats[v]["count"] += 1
        stats[v]["score_sum"] += sc

# -----------------------------
# Сохраняем новый CSV
# -----------------------------
with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["variant", "description", "response", "tokens", "quality_score"])
    writer.writeheader()
    writer.writerows(rows)

# -----------------------------
# Вывод победителя
# -----------------------------
print("=== AUTO-SCORED RESULTS ===")
winner = None
best_avg = -1

for v, s in stats.items():
    avg = s["score_sum"] / s["count"]
    print(f"Variant {v}: count={s['count']}, avg_score={avg:.2f}")
    if avg > best_avg:
        best_avg = avg
        winner = v

print(f"\nWINNER: Variant {winner} (avg_score={best_avg:.2f})")
print(f"Saved: {OUTPUT_CSV}")

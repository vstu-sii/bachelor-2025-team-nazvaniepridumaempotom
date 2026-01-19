import json
import csv
from collections import defaultdict

INPUT_FILE = "data/ab_test_results.jsonl"
OUTPUT_CSV = "data/ab_results_analysis.csv"

# -----------------------------
# 1) Собираем статистику
# -----------------------------
stats = defaultdict(lambda: {"count": 0, "tokens_sum": 0})

rows = []
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        variant = obj["variant"]

        # ТВОЙ формат
        tokens = obj.get("total_tokens", 0)

        stats[variant]["count"] += 1
        stats[variant]["tokens_sum"] += tokens

        rows.append({
            "variant": variant,
            "description": obj["description"],
            "response": obj["evaluation"],
            "tokens": tokens,
            "quality_score": ""  # сюда ты будешь вручную писать 0..5
        })

# -----------------------------
# 2) Считаем средние токены
# -----------------------------
print("\n=== A/B analysis ===")
for v, s in stats.items():
    avg_tokens = s["tokens_sum"] / s["count"]
    print(f"Variant {v}: count={s['count']}, avg_tokens={avg_tokens:.1f}")

# -----------------------------
# 3) Сохраняем CSV для ручной оценки
# -----------------------------
with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["variant", "description", "response", "tokens", "quality_score"])
    writer.writeheader()
    writer.writerows(rows)

print(f"\nCSV saved: {OUTPUT_CSV}")
print("Открой CSV и поставь quality_score (0..5) вручную.")

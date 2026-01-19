import pandas as pd

INPUT_CSV = "data/ab_results_scored.csv"

df = pd.read_csv(INPUT_CSV)

# Средняя оценка по варианту
result = df.groupby("variant")["quality_score"].mean().reset_index()

print("\n=== A/B Winner ===")
print(result)

winner = result.sort_values("quality_score", ascending=False).iloc[0]
print(f"\nWinner: {winner['variant']} (avg score={winner['quality_score']:.2f})")

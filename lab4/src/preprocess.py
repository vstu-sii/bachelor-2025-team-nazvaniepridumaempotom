import os
import json
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"

CSV_PATH = os.path.join(RAW_DIR, "Food Ingredients and Recipe Dataset with Image Name Mapping.csv")
IMG_DIR = os.path.join(RAW_DIR, "Food Images")


def load_data():
    print("Loading CSV...")
    df = pd.read_csv(CSV_PATH)
    print("Loaded:", len(df))
    return df


def row_to_record(row):
    """Преобразуем строку из CSV в единый формат"""

    image_name = str(row["Image_Name"]).strip()
    image_path = os.path.join(IMG_DIR, image_name)

    # Проверяем файл (он может отсутствовать у некоторых строк)
    if not os.path.exists(image_path):
        image_path = None

    # id берём из Unnamed: 0
    uid = int(row["Unnamed: 0"]) if "Unnamed: 0" in row else None

    # очищенные ингредиенты предпочтительнее, если есть
    ingredients = str(row["Cleaned_Ingredients"]).strip()
    if ingredients.lower() == "nan" or not ingredients:
        ingredients = str(row["Ingredients"]).strip()

    return {
        "id": uid,
        "title": str(row["Title"]).strip(),
        "ingredients": ingredients,
        "instructions": str(row["Instructions"]).strip(),
        "image": image_path
    }


def validate_image(path):
    if path is None:
        return False
    try:
        Image.open(path).verify()
        return True
    except Exception:
        return False


def preprocess():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = load_data()

    processed = []

    print("Processing rows...")
    for _, row in df.iterrows():
        rec = row_to_record(row)

        # Пропускаем пустые записи
        if not rec["ingredients"] or not rec["instructions"]:
            continue

        # Проверяем изображение
        if rec["image"] and not validate_image(rec["image"]):
            rec["image"] = None

        processed.append(rec)

    print(f"Valid records: {len(processed)}")

    # Сохраняем общий jsonl
    out_path = os.path.join(OUT_DIR, "recipes_preprocessed.jsonl")
    print("Saving:", out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        for rec in processed:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Разделяем на train/val/test
    print("Splitting dataset...")
    train, temp = train_test_split(processed, test_size=0.2, random_state=42)
    val, test = train_test_split(temp, test_size=0.5, random_state=42)

    for name, data in [("train", train), ("val", val), ("test", test)]:
        split_path = os.path.join(OUT_DIR, f"{name}.jsonl")
        print(f"Saving {name} → {split_path}")
        with open(split_path, "w", encoding="utf-8") as f:
            for rec in data:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("Finished ✔")


if __name__ == "__main__":
    preprocess()

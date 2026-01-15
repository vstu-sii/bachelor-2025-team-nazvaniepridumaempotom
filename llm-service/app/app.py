from fastapi import FastAPI, UploadFile, File
from src.vision_ollama import analyze_image_ollama  # <-- Ollama LLaVA Vision
from src.model_wrapper import llama_generate
import os

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok", "project": "recipe-eval"}


# --------------------------
# 1) Анализ изображения через Ollama LLaVA Vision
# --------------------------
@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    save_path = f"data/raw/{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # Используем Ollama Vision для анализа изображения
    caption = analyze_image_ollama(save_path)

    return {"caption": caption, "file": file.filename}


# --------------------------
# 2) Оценка блюда через LLaMA 3.2 (Ollama или локально)
# --------------------------
@app.post("/evaluate")
async def evaluate(description: str):
    prompt = f"""
Ты — эксперт по еде. Проанализируй описание блюда и оцени его:
1) Дай оценку блюда от 1 до 10.
2) Объясни коротко, почему такая оценка.

Описание блюда:
{description}
    """

    result = llama_generate(prompt)

    return {"llama_response": result}


# --------------------------
# 3) Полный пайплайн: фото → описание → оценка
# --------------------------
@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    save_path = f"data/raw/{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # 1) Получаем описание блюда через Ollama LLaVA Vision
    caption = analyze_image_ollama(save_path)

    # 2) Формируем prompt для LLaMA
    prompt = f"""
Ты — эксперт по еде. Проанализируй описание блюда и оцени его:
1) Дай оценку блюда от 1 до 10.
2) Объясни коротко, почему такая оценка.

Описание блюда:
{caption}
    """

    # 3) Получаем оценку от LLaMA
    evaluation = llama_generate(prompt)

    return {
        "caption": caption,
        "evaluation": evaluation,
        "file": file.filename
    }

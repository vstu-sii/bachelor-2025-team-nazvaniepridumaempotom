# src/vision_ollama.py

import subprocess
from fastapi import HTTPException

def analyze_image_ollama(image_path: str) -> str:
    """
    Анализ изображения через Ollama LLaVA Vision
    """
    try:
        # читаем изображение как байты
        with open(image_path, "rb") as f:
            img_bytes = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения изображения: {e}")

    # формируем запрос для LLaVA (мультимодальный)
    prompt = [
        {"mime_type": "image/jpeg", "data": img_bytes},
        "Опиши, что изображено на фото."
    ]

    result = subprocess.run(
        ["ollama", "run", "llava"],
        input=str(prompt).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Ollama Vision ошибка: {result.stderr.decode()}")

    return result.stdout.decode().strip()

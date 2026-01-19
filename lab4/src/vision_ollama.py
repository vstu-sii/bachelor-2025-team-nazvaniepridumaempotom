import subprocess
import time
import os
from fastapi import HTTPException
from src.langfuse_client import lf


MAX_RETRIES = int(os.getenv("VISION_MAX_RETRIES", 2))
RETRY_DELAY = float(os.getenv("VISION_RETRY_DELAY", 0.5))

MODEL_NAME = os.getenv("VISION_MODEL", "llava")


class DummyContext:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False
    def add_input(self, *args, **kwargs): pass
    def add_output(self, *args, **kwargs): pass


def analyze_image_ollama(image_path: str) -> str:
    try:
        with open(image_path, "rb") as f:
            img_bytes = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения изображения: {e}")

    prompt = [
        {"mime_type": "image/jpeg", "data": img_bytes},
        "Опиши, что изображено на фото."
    ]

    last_error = None

    trace_context = lf.trace("vision_ollama") if lf else DummyContext()

    with trace_context:
        if lf:
            trace_context.add_input("prompt", "image + text")

        for attempt in range(1, MAX_RETRIES + 1):
            start = time.time()

            result = subprocess.run(
                ["ollama", "run", MODEL_NAME],
                input=str(prompt).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            latency = time.time() - start

            if lf:
                trace_context.add_input("attempt", attempt)
                trace_context.add_input("latency_sec", round(latency, 3))

            if result.returncode == 0:
                text = result.stdout.decode().strip()
                if not text:
                    last_error = "Пустой ответ от модели"
                    if lf:
                        trace_context.add_output("status", "error")
                        trace_context.add_output("error", last_error)
                else:
                    if lf:
                        trace_context.add_output("status", "success")
                        trace_context.add_output("caption", text)
                    return text
            else:
                last_error = result.stderr.decode().strip()
                if lf:
                    trace_context.add_output("status", "error")
                    trace_context.add_output("error", last_error)

            time.sleep(RETRY_DELAY)

    raise HTTPException(
        status_code=500,
        detail=f"Ollama Vision ошибка после {MAX_RETRIES} попыток: {last_error}"
    )

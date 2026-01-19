from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from pydantic import BaseModel, Field
from src.vision_ollama import analyze_image_ollama
from src.model_wrapper import llama_generate, SYSTEM_PROMPT
import asyncio
import hashlib
from time import time
import random
import json


app = FastAPI(title="Recipe Evaluation API")
RESULTS_FILE = "data/ab_test_results.jsonl"



# -------------------------
# Validation models
# -------------------------
class TextEvaluationRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Текстовое описание блюда"
    )


class TextEvaluationResponse(BaseModel):
    input_type: str
    description: str
    variant: str
    evaluation: str
    input_tokens: int
    output_tokens: int


# -------------------------
# Cache settings
# -------------------------
CACHE_TTL = 60 * 10  # 10 минут
cache_store = {}


def make_key(text: str, variant: str) -> str:
    return hashlib.sha256(f"{variant}:{text}".encode("utf-8")).hexdigest()


def cache_get(key: str):
    item = cache_store.get(key)
    if not item:
        return None
    value, expires = item
    if time() > expires:
        del cache_store[key]
        return None
    return value


def cache_set(key: str, value: str, ttl: int = CACHE_TTL):
    cache_store[key] = (value, time() + ttl)


# -------------------------
# Rate limiting settings
# -------------------------
RATE_LIMIT = 100          # 5 до, 100 для тестирования
RATE_LIMIT_WINDOW = 60  # секунд

rate_limit_store = {}

def save_result(obj: dict):
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def check_rate_limit(client_id: str):
    now = time()
    window_start = now - RATE_LIMIT_WINDOW

    requests = rate_limit_store.get(client_id, [])

    # оставляем только запросы в текущем окне
    requests = [ts for ts in requests if ts > window_start]

    if len(requests) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )

    requests.append(now)
    rate_limit_store[client_id] = requests


# -------------------------
# Service health check
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------
# Text evaluation
# -------------------------
@app.post(
    "/evaluate/text",
    response_model=TextEvaluationResponse,
    summary="Оценка блюда по текстовым описанию"
)
async def evaluate_text(
    request: TextEvaluationRequest,
    http_request: Request
):
    client_ip = http_request.client.host
    check_rate_limit(client_ip)

    # -------------------------
    # A/B variant
    # -------------------------
    #variant = random.choice(["A", "B"])
    variant = "C"

    system_prompt = (
        "Ты — эксперт по еде. Проанализируй описание блюда и оцени его. "
        "Дай оценку от 1 до 10 и коротко объясни почему."
    )

    # -------------------------
    # caching logic
    # -------------------------
    key = make_key(request.description, variant)
    cached = cache_get(key)

    if cached:
        result = cached
    else:
        result = await asyncio.to_thread(
            llama_generate,
            system_prompt,
            request.description,
            variant  # передаём variant в llama_generate
        )
        cache_set(key, result)

    return {
        "input_type": "text",
        "description": request.description,
        "variant": variant,
        "evaluation": result["text"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "total_tokens": result["input_tokens"] + result["output_tokens"]
    }


# -------------------------
# Image analysis
# -------------------------
@app.post("/analyze/image", summary="Анализ изображения блюда")
async def analyze_image(file: UploadFile = File(...)):
    save_path = f"data/raw/{file.filename}"

    with open(save_path, "wb") as f:
        f.write(await file.read())

    caption = await asyncio.to_thread(
        analyze_image_ollama,
        save_path
    )

    return {
        "input_type": "image",
        "file": file.filename,
        "caption": caption
    }


# -------------------------
# Image evaluation
# -------------------------
@app.post("/evaluate/image", summary="Оценка блюда по изображению")
async def evaluate_image(file: UploadFile = File(...)):
    save_path = f"data/raw/{file.filename}"

    with open(save_path, "wb") as f:
        f.write(await file.read())

    caption = await asyncio.to_thread(
        analyze_image_ollama,
        save_path
    )

    # один вызов модели
    result = await asyncio.to_thread(
        llama_generate,
        SYSTEM_PROMPT,
        caption,
        "A"  # Для image фиксируем вариант A
    )

    return {
        "input_type": "image",
        "file": file.filename,
        "caption": caption,
        "evaluation": result["text"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"]
    }


# -------------------------
# Metrics / evaluation collector
# -------------------------
@app.post("/evaluate/text/metrics", summary="Оценка + метрики токенов")
async def evaluate_text_metrics(
    request: TextEvaluationRequest,
    http_request: Request
):
    client_ip = http_request.client.host
    check_rate_limit(client_ip)

    variant = random.choice(["A", "B", "C"])

    result = await asyncio.to_thread(
        llama_generate,
        SYSTEM_PROMPT,
        request.description,
        variant
    )

    return {
        "input_type": "text",
        "description": request.description,
        "variant": variant,
        "evaluation": result["text"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "total_tokens": result["input_tokens"] + result["output_tokens"]
    }

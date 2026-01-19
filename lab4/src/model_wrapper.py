import subprocess
import time
import os
from typing import Dict

from fastapi import HTTPException
from src.langfuse_client import lf

MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", 2))
RETRY_DELAY = float(os.getenv("LLM_RETRY_DELAY", 0.5))

MODEL_NAME = os.getenv("LLM_MODEL", "llama3.2:1b")
MAX_TOKENS = os.getenv("LLM_MAX_TOKENS", "60")
TEMPERATURE = os.getenv("LLM_TEMPERATURE", "0.2")

# -------------------------
# Prompt variants (user prompt)
# -------------------------
PROMPT_A = (
    "Ты — эксперт по еде. Проанализируй описание блюда и оцени его. "
    "Дай оценку от 1 до 10 и коротко объясни почему."
)

PROMPT_B = (
    "Ты — эксперт по еде. Проанализируй описание блюда и оцени его.\n"
    "Формат ответа:\n"
    "1) Оценка (1-10)\n"
    "2) Короткое объяснение (2-3 предложения)\n"
    "3) 3 ключевых факта из описания\n"
)

#PROMPT_C = (
#    "Ты — эксперт по еде. Проанализируй описание блюда и оцени его.\n"
#    "Ответ должен быть строго в формате:\n"
#    "Оценка: <число от 1 до 10>\n"
#    "Объяснение: <2 коротких предложения>\n"
#    "Не добавляй ничего лишнего.\n"
#    "Старайся отвечать максимально кратко."
#)

PROMPT_C = (
    "Ты — эксперт по еде. Оцени блюдо по описанию (баланс, ингредиенты).\n"
    "Ответ строго в формате (только 2 предложения на русском, без списков):\n"
    "Оценка: <число 1-10>\n"
    "Объяснение: <2 коротких предложения>\n"
    "Если в описании нет данных о вкусе/составе — напиши 'недостаточно данных' во втором предложении.\n"
    "Никакого английского, никаких списков, никаких маркеров, только 2 предложения."
)


# Системный промт (не трогаем)
SYSTEM_PROMPT = (
    "Ты — эксперт по еде. Проанализируй описание блюда и оцени его. "
    "Дай оценку от 1 до 10 и коротко объясни почему."
)

def is_valid_format(text: str) -> bool:
    return "Оценка:" in text and "Объяснение:" in text

def llama_generate(system: str, user: str, variant: str = "A") -> dict[str, int | str]:

    if variant == "A":
        user_prompt = PROMPT_A
    elif variant == "B":
        user_prompt = PROMPT_B
    else:
        user_prompt = PROMPT_C

    full_user = f"{user_prompt}\n\n{user}"

    full_prompt = f"<|system|>\n{system}\n<|user|>\n{full_user}"
    last_error = None

    if lf:
        trace_context = lf.trace("llama_generate")
    else:
        trace_context = None

    with trace_context if trace_context else DummyContext():
        if lf:
            trace_context.add_input("variant", variant)
            trace_context.add_input("system", system)
            trace_context.add_input("user", user)

        for attempt in range(1, MAX_RETRIES + 1):
            start = time.time()

            result = subprocess.run(
                [
                    "ollama", "run", MODEL_NAME,
                    "--max_tokens", MAX_TOKENS,# закомменчено для аб тестирования, раскомментить для улучшения
                    "--temperature", TEMPERATURE # и это тоже
                ],
                input=full_prompt.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            latency = time.time() - start

            if lf:
                trace_context.add_input("attempt", attempt)
                trace_context.add_input("latency_sec", round(latency, 3))

            if result.returncode == 0:
                text = result.stdout.decode().strip()

                # ---- сокращение длины ответа (токены/символы) ----
                MAX_OUTPUT_CHARS = 280
                if len(text) > MAX_OUTPUT_CHARS:
                    text = text[:MAX_OUTPUT_CHARS].rsplit("\n", 1)[0]

                if not is_valid_format(text):
                    # если формат неверный — пометим как ошибка
                    last_error = "Неверный формат ответа"
                    if lf:
                        trace_context.add_output("status", "error")
                        trace_context.add_output("error", last_error)
                    continue  # попробуем ещё раз (если есть retries)

                if not text:
                    last_error = "Пустой ответ от модели"
                    if lf:
                        trace_context.add_output("status", "error")
                        trace_context.add_output("error", last_error)
                else:
                    if lf:
                        trace_context.add_output("status", "success")
                        trace_context.add_output("response", text)
                        trace_context.add_output("input_tokens", len(full_prompt.split()))
                        trace_context.add_output("output_tokens", len(text.split()))

                    return {
                        "text": text,
                        "input_tokens": len(full_prompt.split()),
                        "output_tokens": len(text.split()),
                        "latency_sec": latency
                    }


            else:
                last_error = result.stderr.decode().strip()
                if lf:
                    trace_context.add_output("status", "error")
                    trace_context.add_output("error", last_error)

            time.sleep(RETRY_DELAY)

    raise HTTPException(
        status_code=500,
        detail=f"LLM ошибка после {MAX_RETRIES} попыток: {last_error}"
    )


class DummyContext:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False
    def add_input(self, *args, **kwargs): pass
    def add_output(self, *args, **kwargs): pass

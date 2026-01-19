import json


def load_prompt(path: str):
    """
    Загружает русский промпт из JSON.
    Формат:
    {
        "system": "...",
        "user": "..."
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Проверим что нужные поля есть
    if "system" not in data or "user" not in data:
        raise ValueError(f"Файл промпта {path} должен содержать ключи 'system' и 'user'")

    return data["system"], data["user"]

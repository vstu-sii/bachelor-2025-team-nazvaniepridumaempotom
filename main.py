# main.py
import subprocess
import sys
import os

# -----------------------------
# 1) Проверяем, что мы в .venv
# -----------------------------
venv_path = os.path.join(os.path.dirname(__file__), ".venv")
if not os.path.exists(venv_path):
    print("Warning: .venv не найден, проверьте окружение")
else:
    print(f".venv найден: {venv_path}")

# -----------------------------
# 2) Устанавливаем зависимости (только если есть requirements.txt)
# -----------------------------
req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(req_file):
    print("Устанавливаю зависимости...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file])
else:
    print("requirements.txt не найден — пропускаем установку зависимостей")

# -----------------------------
# 3) Запуск FastAPI
# -----------------------------
print("Запускаю FastAPI...")
subprocess.run([sys.executable, "-m", "uvicorn", "src.app:app", "--reload", "--port", "8001"])

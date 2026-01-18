FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости для Debian
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    netcat-openbsd \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
# COPY requirements.txt .

# # Устанавливаем Python зависимости
# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Настраиваем PYTHONPATH для корректных импортов
ENV PYTHONPATH=/app:/app

# Создаем директорию для логов
RUN mkdir -p /app/logs

EXPOSE 8000

# Команда запуска - исправлена для вашей структуры
# Ваш app находится в api.main, а не просто main
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
FROM python:3.11-slim-bookworm

WORKDIR /app

# Устанавливаем только необходимые зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip

# Копируем зависимости проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем дополнительные зависимости для работы с изображениями
RUN pip install --no-cache-dir \
    pillow \
    opencv-python-headless \
    numpy \
    scikit-image

# Копируем исходный код
COPY app/ /app/
# COPY models/ /app/models/
# COPY notebooks/ /app/notebooks/

# Создаем необходимые директории
RUN mkdir -p /app/uploads /app/logs /app/cache /app/temp

EXPOSE 8001

CMD ["python", "main.py"]
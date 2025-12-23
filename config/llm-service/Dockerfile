# Dockerfile
FROM python:3.11-slim

# Устанавливаем системные зависимости для работы с изображениями
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Копируем исходный код
COPY . .

# Скачиваем модели при сборке (можно вынести в отдельный скрипт)
RUN ollama pull llava:latest && \
    ollama pull llama3.2:1b

# Запускаем Ollama сервис и наше приложение
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001 11434
ENTRYPOINT ["/entrypoint.sh"]
#!/bin/bash
# entrypoint.sh

# Запускаем Ollama в фоновом режиме
ollama serve &

# Ждем запуска Ollama
sleep 10

# Проверяем, что модели доступны
ollama list

# Запускаем наше приложение
python main.py
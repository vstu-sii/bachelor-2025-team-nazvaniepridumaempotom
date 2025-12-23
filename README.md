для работы необходимо установить Ollama и скачать 2 модели через терминал:
ollama pull llava:latest
ollama pull llama3.2:1b

создаём виртуальное окружение:
python -m venv .venv
# source .venv/bin/activate   # для macOS / Linux
# .venv\Scripts\activate    # для Windows

устанавливаем зависимости:
pip install -r requirements.txt

запускаем:
python main.py

сервер доступен по ссылке:
http://127.0.0.1:8001/

POST /analyze-image - анализ изображения
POST /evaluate - оценка текста (передаём описание, возвращает оценку)
POST /process-image - полный пайплайн (загружаем изображение, возвращает результат оценки)

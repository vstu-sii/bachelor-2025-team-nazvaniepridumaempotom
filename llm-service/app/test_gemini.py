import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()  # загружает переменные из .env

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content(
    "Привет! Скажи что-нибудь :)",
    max_output_tokens=20  # ограничиваем длину ответа
)


print(response.text)

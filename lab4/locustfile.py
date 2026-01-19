from locust import HttpUser, task, between
import random

DESCRIPTIONS = [
    "Паста карбонара с беконом и пармезаном",
    "Салат с курицей, огурцом и помидорами",
    "Бургер с говядиной и сыром",
    "Пицца маргарита с моцареллой",
    "Суп из тыквы со сливками"
]

class RecipeUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def evaluate_text(self):
        payload = {
            "description": random.choice(DESCRIPTIONS)
        }

        self.client.post(
            "/evaluate/text",
            json=payload
        )

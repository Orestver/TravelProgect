from google import genai
from config import GEMINI_API

class TravelAssistant:
    def __init__(self, name, destination, style, days, language="Українська"):
        self.client = genai.Client(api_key=GEMINI_API)
        self.name = name
        self.destination = destination
        self.style = style
        self.days = days
        self.language = language

    def generate_recommendations(self):
        prompt = (
            f"You are a caring and knowledgeable travel planning assistant with an outgoing and funny personality. "
            f"My name is {self.name}. I am planning to travel to {self.destination} in {self.style} style "
            f"for {self.days} days. "
            f"Write the response in {self.language} language. "
            f"Describe what to do each day in detail."
        )

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text


def main():
    print("=== Travel Plan Assistant ===")
    name = input("Ваше ім'я: ").strip()
    destination = input("Куди плануєте поїхати?: ").strip()
    style = input("Опишіть стиль подорожі (наприклад, активний, розслаблений): ").strip()
    days = input("На скільки днів поїздка?: ").strip()
    language = input("Мова (Українська або English): ").strip()

    assistant = TravelAssistant(name, destination, style, days, language)
    plan = assistant.generate_recommendations()

    print("\n=== Ваш план подорожі ===\n")
    print(plan)


if __name__ == "__main__":
    main()

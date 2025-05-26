import requests
from urllib.parse import quote
from config import WEATHER_API

# Define a mapping for transliteration
transliteration_map = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
    'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '',
    'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}

def transliterate(text):
    transliterated_text = []
    for char in text:
        transliterated_char = transliteration_map.get(char, char)
        transliterated_text.append(transliterated_char)
    return ''.join(transliterated_text)

class WeatherForecast:
    def get_weather(self, city):
        if not city:
            return
        try:
            city_encoded = quote(transliterate(city))
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={WEATHER_API}&units=metric"
            response = requests.get(url)
            data = response.json()

            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]

            message = (
                f"Weather in {city}:\n"
                f"Temp: {temp}°C\n"
                f"Desc: {description}\n"
                f"Humidity: {humidity}%\n"
            )
            print(message)

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    city = input("Введіть місто: ")
    weather = WeatherForecast()
    weather.get_weather(city)

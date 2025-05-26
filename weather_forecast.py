import requests
from urllib.parse import quote
from config import WEATHER_API

class WeatherForecast:
    def init(self, parent=None, label=None):
        self.parent = parent
        self.label = label  

    def transliterate_city_name(self, city_name):
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g',
            'д': 'd', 'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z',
            'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k',
            'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
            'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
            'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ь': '', 'ю': 'iu', 'я': 'ia', '’': '', "'": ''
        }
        return ''.join(translit_map.get(c, c) for c in city_name.lower())

    def get_weather(self, city):
        if not city:
            if self.label:
                self.label.setText("⚠️ Введіть назву міста.")
            return

        try:
            city_latin = self.transliterate_city_name(city)
            city_encoded = quote(city_latin)
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={WEATHER_API}&units=metric&lang=ua"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") != 200:
                if self.label:
                    self.label.setText(f"❌ Місто «{city}» не знайдено (код: {data.get('cod')})")
                return

            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            message = (
                f"📍 Погода в {city}:\n"
                f"🌡 Температура: {temp}°C\n"
                f"☁️ Опис: {weather.capitalize()}\n"
                f"💧 Вологість: {humidity}%\n"
                f"💨 Вітер: {wind_speed} м/с"
            )

            if self.label:
                self.label.setText(message)
            else:
                print(message)

        except requests.exceptions.RequestException as e:
            if self.label:
                self.label.setText(f"❌ Проблема з'єднання: {str(e)}")
            else:
                print(f"❌ Проблема з'єднання: {str(e)}")
        except Exception as e:
            if self.label:
                self.label.setText(f"⚠️ Помилка: {str(e)}")
            else:
                print(f"⚠️ Помилка: {str(e)}")

if name == "main":
    city = input("Введіть місто: ")
    weather = WeatherForecast()
    weather.get_weather(city)

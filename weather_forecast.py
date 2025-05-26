import requests
from urllib.parse import quote
from config import WEATHER_API

class WeatherForecast:
    def get_weather(self, city):
        if not city:
            return
        try:
            city_encoded = quote(city)
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
            
        except:
            print("error")


if __name__ == "__main__":
    city = input("Введіть місто ")
    weather  = WeatherForecast()
    weather.get_weather(city)

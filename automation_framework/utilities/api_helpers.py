import requests
from .config_loader import load_config

class ApiHelper:
    def __init__(self):
        """
        Initialize the API helper by loading configuration from the specified file.
        """
        self.config = load_config()

        # Retrieve API details from the config file
        self.BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
        self.API_KEY = self.config.get("API", "API_KEY").strip()

    def get_current_weather(self, city, units="metric", lang="en"):
        url = f"{self.BASE_URL}?q={city}&appid={self.API_KEY}&units={units}&lang={lang}"
        print(url)
        response = requests.get(url)
        print(response)
        return response

    def get_weather_by_city_id(self, city_id, units="metric", lang="en"):
        """Fetch weather data for a city using its ID."""
        url = f"{self.BASE_URL}?id={city_id}&appid={self.API_KEY}&units={units}&lang={lang}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch weather for city ID {city_id}: {response.status_code}")
            return None

        data = response.json()
        weather_data = {
            "city_id": city_id,
            "city_name": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "avg_temperature": round((data["main"]["temp_min"] + data["main"]["temp_max"]) / 2, 2)
        }
        return weather_data

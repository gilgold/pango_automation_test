import json
import requests
from ..utilities.api_helpers import ApiHelper
from ..utilities.db_helpers import DatabaseHelper
from selenium_scraper import WeatherScraper


def fetch_cities_from_openweathermap():
    # URL for the city list file
    city_list_url = "http://bulk.openweathermap.org/sample/city.list.json.gz"
    response = requests.get(city_list_url)
    if response.status_code == 200:
        # Uncompress and load JSON
        import gzip
        import io
        with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
            city_data = json.load(f)

        # Extract first 100 cities
        cities = [{"id": city["id"], "city_name": city["name"], "country": city["country"]} for city in city_data[:100]]
        print(f"Loaded {len(cities)} cities.")
        return cities
    else:
        print(f"Failed to fetch city list. Status Code: {response.status_code}")
        return []

def perform_temperature_analysis():
    # Initialize helpers
    api_helper = ApiHelper()
    db_helper = DatabaseHelper()
    scraper = WeatherScraper()

    # Load city data
    cities = fetch_cities_from_openweathermap()

    for city in cities[:100]:  # Limit to 100 cities for this analysis
        city_name = city["city_name"]
        print(f"Processing {city_name}...")

        # Fetch temperature from OpenWeatherMap
        api_response = api_helper.get_current_weather(city_name)
        if not api_response or api_response.status_code != 200 or "main" not in api_response:
            print(f"Skipping {city_name} due to API issues.")
            continue
        api_temp = api_response["main"]["temp"]

        # Fetch temperature from Time and Date website
        website_temp = scraper.get_temperature(city_name)
        if website_temp is None:
            print(f"Skipping {city_name} due to scraping issues.")
            continue

        # Calculate difference and store in database
        difference = abs(api_temp - website_temp)
        db_helper.insert_discrepancy_data(city_name, api_temp, website_temp, difference)

    scraper.close()
    print("Temperature analysis completed.")

import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from utilities.api_helpers import ApiHelper
from utilities.db_helpers import DatabaseHelper
from utilities.weather_analysis.scrapers.web.selenium_scraper import WeatherScraper
from utilities.weather_analysis.scrapers.android.android_scraper import AndroidScraper


def fetch_cities_from_openweathermap(limit: int):
    # Option 1 - get 100 cities from the openweathermap bulk file

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
        cities = [{"id": city["id"], "city_name": city["name"], "country": city["country"]} for city in city_data[:limit]]
        print(f"Loaded {len(cities)} cities.")
        return cities
    else:
        print(f"Failed to fetch city list. Status Code: {response.status_code}")
        return []

def fetch_cities_from_time_and_date(limit: int):
    # Option 2 - get at least <limit> cities of the table in www.timeanddate.com/weather
    driver = webdriver.Chrome()
    driver.get("https://www.timeanddate.com/weather/")

    # Navigate to the region with cities
    cities = []
    try:
        city_links = driver.find_elements(By.CSS_SELECTOR, ".zebra.fw.tb-theme tbody tr a")
        for link in city_links[:limit]:  # Limit to 100 cities
            cities.append(link.text)
    except Exception as e:
        print(f"Error scraping city names: {e}")
    finally:
        driver.quit()

    print(f"Fetched {len(cities)} cities.")
    return cities

def perform_temperature_analysis(use_android_app: bool = False, limit: int = 100):
    # This method can compare data to the website or and android app

    # Initialize helpers
    api_helper = ApiHelper()
    db_helper = DatabaseHelper()

    # Choose appium or web scraper
    if use_android_app:
        scraper = AndroidScraper()
    else:
        scraper = WeatherScraper()

    # Load city data
    cities = fetch_cities_from_time_and_date(limit)

    for city_name in cities[:limit]:  # Limit number of cities for this analysis
        print(f"Processing {city_name}...")

        # Fetch temperature from OpenWeatherMap
        api_response = api_helper.get_current_weather(city_name)

        if not api_response or api_response.status_code != 200:
            print(f"Skipping {city_name} due to API issues.")
            continue
        weather_data = json.loads(api_response.text)
        api_temp = weather_data["main"]["temp"]

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

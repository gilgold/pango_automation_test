import json
import os
import pytest
from automation_framework.utilities.api_helpers import ApiHelper
from db_connection import DatabaseConnection
from ..utilities.db_helpers import DatabaseHelper


def city_data():
    """Load mock city data from the JSON file."""
    folder_path = os.path.abspath(os.path.dirname(__file__))
    folder = os.path.join(folder_path, 'mock_data')
    jsonfile = os.path.join(folder, "cities.json")
    with open(jsonfile, "r") as file:
        return json.load(file)



@pytest.fixture(scope="module")
def api():
    """
    Fixture to provide an instance of ApiHelper for API-related tests.
    """
    return ApiHelper()

@pytest.fixture(scope="module")
def db_helper(api):
    """
    Fixture to provide an instance of DatabaseHelper for database-related tests.
    Ensures the database connection is closed after tests.
    """
    db = DatabaseHelper()
    # Ensure the database starts clean for tests
    seed_db(api, db)
    yield db
    DatabaseConnection.close_connection()  # Close the database connection after all tests in the module are done# Cleanup the database connection

def seed_db(api, db_helper):
    # Seed the db with some data from mock cities and get weather data for each one
    db_helper.clear_weather_data()
    for city in city_data():
        city_id = city["city_id"]
        weather_data = api.get_weather_by_city_id(city_id)

        # Insert data into the database
        db_helper.insert_weather_data(
            weather_data["city_id"],
            weather_data["city_name"],
            weather_data["temperature"],
            weather_data["feels_like"],
            weather_data["avg_temperature"],
        )

def test_get_current_weather(api, db_helper):
    city = "London"
    current_weather_response = api.get_current_weather(city)
    assert current_weather_response.status_code == 200
    weather_data = json.loads(current_weather_response.text)
    assert "temp" in weather_data["main"], f"Missing 'temp' (temperature) in response for {city}."
    assert "feels_like" in weather_data["main"], f"Missing 'feels_like' in response for {city}."

    # Extract temperature and feels_like from the API response
    city_id = weather_data["id"]
    temperature = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]

    db_data = db_helper.get_weather_data(city_id)
    assert db_data is not None, f"No data found in the database for {city}."
    db_city_name, db_temperature, db_feels_like, _ = db_data

    # Validate that the temperature and feels_like in the database match the API response
    assert db_city_name == city, f"City name mismatch. DB: {db_city_name}, API: {city}."


    # Since this test is for testing the weather?q=city_name (get_current_weather) api and
    # db_seed uses "get by city_id" (get_weather_by_city_id) api this assertion will almost always fail
    # since the 2 endpoints do not return the same value. I would remove one of the methods -
    # either the one to get by city_id or the one by city_name but this was not part of the assignment
    assert db_temperature == temperature, (
        f"Temperature mismatch for {city}. DB: {db_temperature}, API: {temperature}."
    )
    assert db_feels_like == feels_like, (
        f"Feels_like mismatch for {city}. DB: {db_feels_like}, API: {feels_like}."
    )

@pytest.mark.parametrize("city", [
    pytest.param(city, id=city['city_name']) for city in city_data()
])
def test_get_weather_data(api, db_helper, city):
    """
    Test to validate weather data by city ID:
    - Fetches weather data from the API.
    - Validates that database values match API response.
    """
    city_id, city_name = city["city_id"], city["city_name"]

    # Fetch weather data from the API
    weather_data = api.get_weather_by_city_id(city_id)

    # Validate API response
    assert weather_data is not None, f"Failed to fetch weather data for city {city_name}."
    assert "temperature" in weather_data and "feels_like" in weather_data, (
        f"Weather data for {city_name} is missing required fields."
    )

    # Retrieve data from the database
    db_data = db_helper.get_weather_data(city_id)
    assert db_data is not None, f"No data found in the database for city {city_name}."
    db_city_name, db_temperature, db_feels_like, db_avg_temperature = db_data

    # Validate database values match API response
    assert db_city_name == weather_data["city_name"], (
        f"City name mismatch. DB: {db_city_name}, API: {weather_data['city_name']}."
    )
    assert db_temperature == weather_data["temperature"], (
        f"Temperature mismatch for {city_name}. DB: {db_temperature}, API: {weather_data['temperature']}."
    )
    assert db_feels_like == weather_data["feels_like"], (
        f"Feels_like mismatch for {city_name}. DB: {db_feels_like}, API: {weather_data['feels_like']}."
    )
    assert round(db_avg_temperature, 2) == round(weather_data["avg_temperature"], 2), (
        f"Average temperature mismatch for {city_name}. DB: {db_avg_temperature}."
    )

def test_section_2_print_highest_avg_temperature(api, db_helper):
    """
    Print the city with the highest temperature
    """
    city, highest_temp = db_helper.get_city_with_highest_avg_temperature()
    print(f"City: {city}, Highest Avg Temperature: {highest_temp}")




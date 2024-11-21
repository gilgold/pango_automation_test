from selenium import webdriver
from selenium.webdriver.common.by import By

from utilities.weather_analysis.scrapers.base_scraper import Scraper

WAIT_TIMEOUT = 10

class WeatherScraper(Scraper):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(WAIT_TIMEOUT)

    def get_temperature(self, city):
        try:
            self.driver.get("https://www.timeanddate.com/weather/")
            # city_link = self.driver.find_element(By.CSS_SELECTOR, f"a[href*='{city.lower().replace(' ', '-')}']")
            city_link = self.driver.find_element(By.XPATH, f"//*[contains(text(), \"{city}\")]")
            city_link.click()

            # Extract the temperature value
            temp_element = self.driver.find_element(By.CSS_SELECTOR, "#qlook .h2")
            temp_text = temp_element.text.split()[0].strip()
            return float(temp_text)
        except Exception as e:
            print(f"Error fetching temperature for {city}: {e}")
            return None

    def close(self):
        self.driver.quit()

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from time import sleep

from typing import Optional

from utilities.weather_analysis.scrapers.base_scraper import Scraper


class AndroidScraper(Scraper):
    def __init__(self):
        capabilities = dict(
            platformName='Android',
            automationName='uiautomator2',
            deviceName='Android',
            appPackage='com.android.settings',
            appActivity='.Settings',
            language='en',
            locale='US'
        )

        # Initialize Appium driver
        self.driver = webdriver.Remote("http://localhost:4723/wd/hub")
        self.driver.caps = capabilities

    def get_temperature(self, city: str) -> Optional[float]:
        try:
            # Wait for the app to load
            sleep(5)

            # Search for the city by interacting with the search box (if available)
            search_box = self.driver.find_element(AppiumBy.ID, "com.android.searchbox")  # Update this ID if needed
            search_box.click()

            # Enter the city name
            search_box.send_keys(city)
            sleep(2)  # Wait for the search results to load

            # Click on the city name from the results
            city_result = self.driver.find_element(AppiumBy.XPATH, f"//android.widget.TextView[@text='{city}']")
            city_result.click()

            # Wait for the weather details to load
            sleep(3)

            # Find the temperature element in the app (adjust the XPath as necessary)
            temp_element = self.driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@content-desc='temperature']")
            temperature = temp_element.text  # Get the temperature as text

            print(f"Temperature for {city}: {temperature}°C")
            return float(temperature)
        except Exception as e:
            print(f"Error fetching temperature for {city}: {e}")
            return None
        finally:
            self.close()

    def close(self):
        self.driver.quit()
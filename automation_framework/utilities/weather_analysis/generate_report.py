from utilities.weather_analysis.data_discrepancy_analysis_script import perform_temperature_analysis
from automation_framework.utilities.db_helpers import DatabaseHelper

def generate_report(use_android_app: bool, limit: int):

    perform_temperature_analysis(use_android_app, limit)

    db_helper = DatabaseHelper()

    results = db_helper.get_discrepancy()

    print(f"{len(results)} Cities with significant temperature discrepancies:")
    for row in results:
        city, api_temp, website_temp, difference = row
        print(f"{city}: API Temp = {api_temp}°C, Website Temp = {website_temp}°C, Difference = {difference}°C")


def generate_web_report():
    generate_report(False, 100)

def generate_android_report():
    generate_report(True, 20)

# Ensure the script runs only when executed directly, not when imported
if __name__ == "__main__":
    generate_web_report()
    # TODO: fix appium issues and get proper selectors for elements
    # generate_android_report()

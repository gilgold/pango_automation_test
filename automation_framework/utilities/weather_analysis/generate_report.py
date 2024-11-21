from weather_analysis.data_discrepancy_analysis_script import perform_temperature_analysis
from . import DatabaseHelper

def generate_report():

    perform_temperature_analysis()

    db_helper = DatabaseHelper()

    results = db_helper.get_discrepancy()

    print("Cities with significant temperature discrepancies:")
    for row in results:
        city, api_temp, website_temp, difference = row
        print(f"{city}: API Temp = {api_temp}°C, Website Temp = {website_temp}°C, Difference = {difference}°C")

# Ensure the script runs only when executed directly, not when imported
if __name__ == "__main__":
    generate_report()

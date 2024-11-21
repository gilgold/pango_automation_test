from db_connection import DatabaseConnection


class DatabaseHelper:
    def __init__(self):
        self.conn = DatabaseConnection.get_connection()
        self.create_tables()

    def create_tables(self):
        """Create tables if they don't exist."""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS weather_data (
                    city_id INTEGER PRIMARY KEY,
                    city_name TEXT,
                    temperature REAL,
                    feels_like REAL,
                    avg_temperature REAL
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS temperature_discrepancies (
                    city TEXT PRIMARY KEY,
                    api_temp REAL,
                    website_temp REAL,
                    difference REAL
                )
            ''')

    def insert_discrepancy_data(self, city, api_temp, website_temp, difference):
        with self.conn:
            self.conn.execute('''
                    INSERT OR REPLACE INTO temperature_discrepancies (city, api_temp, website_temp, difference)
                    VALUES (?, ?, ?, ?)
                ''', (city, api_temp, website_temp, difference))

    def insert_weather_data(self, city_id, city_name, temperature, feels_like, avg_temperature):
        """Insert or update weather data for a city, including average temperature."""
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO weather_data 
                (city_id, city_name, temperature, feels_like, avg_temperature)
                VALUES (?, ?, ?, ?, ?)
            ''', (city_id, city_name, temperature, feels_like, avg_temperature))

    def get_discrepancy(self):
        with self.conn:
            cursor = self.conn.execute('''
                    SELECT city, api_temp, website_temp, difference
                    FROM temperature_discrepancies
                    WHERE difference > 2
                    ORDER BY difference DESC
                    LIMIT 100
                ''')
            return cursor.fetchall()

    def get_weather_data(self, city_id):
        """Retrieve weather data for a city."""
        with self.conn:
            cursor = self.conn.execute('''
                SELECT city_name, temperature, feels_like, avg_temperature
                FROM weather_data
                WHERE city_id = ?
            ''', (city_id,))
            return cursor.fetchone()

    def get_city_with_highest_avg_temperature(self):
        """Retrieve the city with the highest average temperature."""
        with self.conn:
            cursor = self.conn.execute('''
                SELECT city_name, avg_temperature
                FROM weather_data
                ORDER BY avg_temperature DESC
                LIMIT 1
            ''')
            return cursor.fetchone()

    def clear_weather_data(self):
        """Clears all data from the weather_data table."""
        with self.conn:
            self.conn.execute('DELETE FROM weather_data')

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()

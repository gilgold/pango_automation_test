import os
import sqlite3

from utilities.config_loader import load_config


class DatabaseConnection:
    _connection = None
    _config = load_config()

    @staticmethod
    def get_connection():
        """
        Singleton pattern to ensure a single database connection across the app.
        """
        root_dir = os.path.dirname(os.path.abspath(__file__))  # Adjust based on config folder's location
        db_path = os.path.join(root_dir, DatabaseConnection._config.get("DB", "DB_NAME"))
        if DatabaseConnection._connection is None:
            DatabaseConnection._connection = sqlite3.connect(db_path)
        return DatabaseConnection._connection

    @staticmethod
    def close_connection():
        """
        Close the database connection if it exists.
        """
        if DatabaseConnection._connection:
            DatabaseConnection._connection.close()
            DatabaseConnection._connection = None

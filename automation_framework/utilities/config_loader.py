import configparser
import os


def load_config(file = "../config/config.ini"):
    config = configparser.ConfigParser()

    # Resolve the absolute path of the config file relative to this script's location
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_abs_path = os.path.abspath(os.path.join(base_path, file))

    # Verify the configuration file exists
    if not os.path.exists(config_abs_path):
        raise FileNotFoundError(f"Configuration file not found at {config_abs_path}")

    # Load the configuration file
    config.read(config_abs_path)

    return config
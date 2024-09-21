import requests
import ctypes
import json

ONLINE_CONFIG_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/refs/heads/2.0-dev/data/settings/config.json"
CONFIG_PATH = "data/settings/config.json"

def get_current_version():
    return read()["latest_version"]

def read():
    try:
        with open("data/settings/config.json") as config_file:
            config_data = json.load(config_file)
            if len(config_data) == 0:
                ctypes.windll.user32.MessageBoxW(0, "CONFIG DATA NOT FOUND", "Error", 0)
                exit(1)
            return config_data
    except:
        ctypes.windll.user32.MessageBoxW(0, "CONFIG FILE NOT FOUND", "Error", 0)

def read_remote():
    try:
        online_config_data = requests.get(ONLINE_CONFIG_URL).json()
        if len(online_config_data) == 0:
            ctypes.windll.user32.MessageBoxW(0, "ONLINE CONFIG DATA NOT FOUND", "Error", 0)
            exit(1)
        return online_config_data
    except:
        ctypes.windll.user32.MessageBoxW(0, "ONLINE URL NOT FOUND. CANNOT RUN UPDATE CHECKER", "Error", 0)
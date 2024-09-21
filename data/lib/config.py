from customtkinter import *
import requests
import ctypes
import json


ONLINE_CONFIG_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/refs/heads/2.0-dev/data/settings/config.json"
CONFIG_PATH = "data/settings/config.json"

def get_current_version():
    return read()["version"]

def read(key=""):
    try:
        with open("data/settings/config.json") as config_file:
            config_data = json.load(config_file)
            if len(config_data) == 0:
                ctypes.windll.user32.MessageBoxW(0, "CONFIG DATA NOT FOUND", "Error", 0)
                exit(1)
            if not key == "":
                return config_data[key]
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

def save(config_data):
    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

def generate_tk_list():
    config_data = read()
    tk_var_list = {}
    for key in config_data:
        tk_var_list[key] = StringVar(value=config_data[key])
    return tk_var_list

def save_tk_list(tk_var_list):
    config_data = read()
    for key in tk_var_list:
        config_data[key] = tk_var_list[key].get()
    save(config_data)
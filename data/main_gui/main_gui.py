from customtkinter import *
from time import sleep
import threading
import json
import os

CURRENT_VERSION = "1.3"

class update_window(CTk):
    def __init__(self):
        super().__init__()
        if (not CURRENT_VERSION == config_data["latestversion"]) and (not CURRENT_VERSION == config_data["latestbetaversion"]):
            self.title("You can update!")
            self.geometry("300x100x500x500")
            # FONTS + BUTTON
            current_version_label = CTkLabel(master=self, text=f"Your current version: {CURRENT_VERSION}").pack()
            latest_version_label = CTkLabel(master=self, text=f"Latest version: {config_data["latestversion"]}").pack()

class main_window(CTk):
    def __init__(self):
        super().__init__()
        self.title(f"MACRO NAME v{CURRENT_VERSION}")
        self.geometry("600x300x200x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        set_appearance_mode(config_data["appearance"])
        set_default_color_theme("blue")

        default_font = "Segoe UI"
        default_font_bold = "Segoe UI Semibold"
        max_width = 200

        global tab_control
        tab_control = CTkTabview(master=self, height=290)
        tab_control.grid(padx=10, sticky="ew")
        
        tab_control.add("Main")
        tab_control.add("Crafting")
        tab_control.add("Webhook")
        tab_control.add("Settings")
        tab_control.add("Extras")
        tab_control.add("Credits")

        for button in tab_control._segmented_button._buttons_dict.values():
            button.configure(width=max_width, height=35, corner_radius=7, font=CTkFont(default_font_bold, size=16, weight="bold"))
        
        # Main tab
        # obby_frame = CTkFrame(master=main_tab, width=200, height=70).grid()
        # obby_title_label = CTkLabel(master=obby_frame, text="Obby", font=CTkFont(default_font_bold, size=13, weight="bold")).grid()
    

def read_config():
    with open("data/settings/config.json") as config_file:
        global config_data
        config_data = json.load(config_file)

def create_main_gui():
    update_window().mainloop()
    main_window().mainloop()
    


read_config()
create_main_gui()

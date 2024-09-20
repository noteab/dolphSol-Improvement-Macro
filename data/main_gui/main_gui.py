import customtkinter as ctk
import json
import os

class main_gui(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"MACRO NAME v{config_data["version"]}")
        self.geometry("500x250")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        tab_control = ctk.CTkTabview(master=self, height=240)
        tab_control.grid(padx=10, sticky="ew")

        tab_control.add("Main")
        tab_control.add("Crafting")
        tab_control.add("Webhook")
        tab_control.add("Settings")
        tab_control.add("Extras")
        tab_control.add("Credits")
        tab_control.set("Main")

        for button in tab_control._segmented_button._buttons_dict.values():
            button.configure(width=100, height=30)

def read_config():
    with open("data/settings/config.json") as config_file:
        global config_data
        config_data = json.load(config_file)
    
def create_main_gui():
    app = main_gui()
    app.mainloop()


read_config()

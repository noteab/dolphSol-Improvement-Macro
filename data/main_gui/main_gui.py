# Let's modify the Python script to add the Merchant settings in the "Merchant" tab

import customtkinter as ctk
import json
import os

class main_gui(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window title and dimensions
        self.title(f"dolphSol Macro v{config_data['version']}")
        self.geometry("550x400")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        # Create the tab control
        tab_control = ctk.CTkTabview(master=self, height=240)
        tab_control.grid(padx=10, pady=10, sticky="ew")

        # Add tabs
        tab_control.add("Main")
        tab_control.add("Merchant")
        tab_control.add("Webhook")
        tab_control.add("Settings")
        tab_control.add("Extras")
        tab_control.add("Credits")
        tab_control.set("Main")

        # Customize buttons in the tab control
        for button in tab_control._segmented_button._buttons_dict.values():
            button.configure(width=100, height=30)
            
def read_config():
    with open("data/settings/config.json") as config_file:
        global config_data
        config_data = json.load(config_file)

def create_main_gui():
    app = main_gui()
    app.mainloop()

# Load the configuration and create the GUI
read_config()
create_main_gui()

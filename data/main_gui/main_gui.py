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

        # Create Merchant tab
        self.merchant_tab = tab_control.tab("Merchant")
        self.create_merchant_tab()

    def create_merchant_tab(self):
        # Add a checkbox for Auto Merchant
        self.auto_merchant_check = ctk.CTkCheckBox(self.merchant_tab, text="Enable Auto Merchant", onvalue="ON", offvalue="OFF")
        self.auto_merchant_check.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Merchant Slider Position (X, Y)
        ctk.CTkLabel(self.merchant_tab, text="Merchant Slider Position (X, Y):").grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.merchant_slider_x = ctk.CTkEntry(self.merchant_tab, placeholder_text="X")
        self.merchant_slider_x.grid(row=1, column=1, padx=5, pady=5)
        self.merchant_slider_y = ctk.CTkEntry(self.merchant_tab, placeholder_text="Y")
        self.merchant_slider_y.grid(row=1, column=2, padx=5, pady=5)

        # Purchase Amount Button Position (X, Y)
        ctk.CTkLabel(self.merchant_tab, text="Purchase Amount Button (X, Y):").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.purchase_amount_x = ctk.CTkEntry(self.merchant_tab, placeholder_text="X")
        self.purchase_amount_x.grid(row=2, column=1, padx=5, pady=5)
        self.purchase_amount_y = ctk.CTkEntry(self.merchant_tab, placeholder_text="Y")
        self.purchase_amount_y.grid(row=2, column=2, padx=5, pady=5)

        # Purchase Button Position (X, Y)
        ctk.CTkLabel(self.merchant_tab, text="Purchase Button (X, Y):").grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.purchase_button_x = ctk.CTkEntry(self.merchant_tab, placeholder_text="X")
        self.purchase_button_x.grid(row=3, column=1, padx=5, pady=5)
        self.purchase_button_y = ctk.CTkEntry(self.merchant_tab, placeholder_text="Y")
        self.purchase_button_y.grid(row=3, column=2, padx=5, pady=5)

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

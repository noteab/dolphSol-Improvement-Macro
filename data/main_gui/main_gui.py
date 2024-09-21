from customtkinter import *
import json
import os
import sys

CURRENT_VERSION = "1.3"

# config path checking using os module
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This will get up to the parent folder
CONFIG_PATH = os.path.join(BASE_DIR, 'data', 'settings', 'config.json')


class UpdateWindow(CTk):
    def __init__(self):
        super().__init__()
        self.load_config()
        
        if CURRENT_VERSION == self.config_data["latestversion"] and CURRENT_VERSION == self.config_data["latestbetaversion"]:
            self.destroy()
        else:
            self.title("You can update!")
            self.geometry("300x100")
            CTkLabel(master=self, text=f"Your current version: {CURRENT_VERSION}").pack()
            CTkLabel(master=self, text=f"Latest version: {self.config_data['latestversion']}").pack()

    def load_config(self):
        with open(CONFIG_PATH) as config_file:
            self.config_data = json.load(config_file)


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.title(f"MACRO NAME v{CURRENT_VERSION}")
        self.geometry("600x300")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.set_appearance()

        self.tab_control = CTkTabview(master=self, height=290)
        self.tab_control.grid(padx=10, sticky="ew")

        self.tab_control.add("Main")
        self.tab_control.add("Crafting")
        self.tab_control.add("Webhook")
        self.tab_control.add("Settings")
        self.tab_control.add("Extras")
        self.tab_control.add("Credits")

        self.create_buttons()
        self.create_settings_tab()

        self.bind("<F1>", lambda e: self.start())
        self.bind("<F2>", lambda e: self.pause())
        self.bind("<F3>", lambda e: self.stop())

    def load_config(self):
        with open(CONFIG_PATH) as config_file:
            self.config_data = json.load(config_file)

    def create_buttons(self):
        button_frame = CTkFrame(master=self.tab_control.tab("Main"))
        button_frame.pack(side="bottom", pady=10, fill="x")

        start_button = CTkButton(master=button_frame, text="Start (F1)", command=self.start)
        start_button.pack(side="left", padx=5)

        pause_button = CTkButton(master=button_frame, text="Pause (F2)", command=self.pause)
        pause_button.pack(side="left", padx=5)

        stop_button = CTkButton(master=button_frame, text="Stop (F3)", command=self.stop)
        stop_button.pack(side="left", padx=5)

    def create_settings_tab(self):
        self.theme_var = IntVar(value=1 if self.config_data.get("dark_mode", False) else 2 if self.config_data.get("vibrant_mode", False) else 0)

        customization_label = CTkLabel(master=self.tab_control.tab("Settings"), text="Customization", font=("Segoe UI", 14, "bold"))
        customization_label.pack(pady=(10, 5))

        dark_mode_radio = CTkRadioButton(master=self.tab_control.tab("Settings"), text="Dark Mode", variable=self.theme_var, value=1, command=self.update_theme)
        dark_mode_radio.pack(pady=5)

        vibrant_mode_radio = CTkRadioButton(master=self.tab_control.tab("Settings"), text="Vibrant Mode", variable=self.theme_var, value=2, command=self.update_theme)
        vibrant_mode_radio.pack(pady=5)

    def update_theme(self):
        selected_theme = self.theme_var.get()

        if selected_theme == 1:
            self.config_data["dark_mode"] = True
            self.config_data["vibrant_mode"] = False
            set_appearance_mode("dark")
        elif selected_theme == 2:
            self.config_data["dark_mode"] = False
            self.config_data["vibrant_mode"] = True
            set_appearance_mode("vibrant")  # Ensure you have defined "vibrant" in your theme settings
        else:
            self.config_data["dark_mode"] = False
            self.config_data["vibrant_mode"] = False
            set_appearance_mode("light")

        with open(CONFIG_PATH, 'w') as config_file:
            json.dump(self.config_data, config_file, indent=4)

        self.restart_app()  # Restart the app to apply the changes

    def restart_app(self):
        os.execv(sys.executable, ['python'] + sys.argv)

    def start(self):
        print("Started")

    def pause(self):
        print("Paused")

    def stop(self):
        print("Stopped")

    def set_appearance(self):
        set_appearance_mode("dark" if self.config_data.get("dark_mode", False) else "light")
        set_default_color_theme("blue")

def create_main_gui():
    UpdateWindow().mainloop()
    MainWindow().mainloop()

create_main_gui()

from customtkinter import *
from time import sleep
from data.lib import config

CURRENT_VERSION = config.get_current_version()
DEFAULT_FONT = "Segoe UI"
DEFAULT_FONT_BOLD = "Segoe UI Semibold"
MAX_WIDTH = 1000

config_data = config.read()

class main_window(CTk):
    def __init__(self):
        super().__init__()

        self.title(f"MACRO NAME v{CURRENT_VERSION}")
        self.geometry("600x300x200x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        set_appearance_mode(config_data["appearance"])
        set_default_color_theme("blue")

        tab_control = CTkTabview(master=self, height=290, fg_color="transparent")
        tab_control.grid(padx=10, sticky="ew")
        
        main_tab = tab_control.add("Main")
        crafting_tab = tab_control.add("Crafting")
        webhook_tab = tab_control.add("Webhook")
        settings_tab = tab_control.add("Settings")
        extras_tab = tab_control.add("Extras")
        credits_tab = tab_control.add("Credits")
        
        credits_tab = tab_control.set("Credits")

        for button in tab_control._segmented_button._buttons_dict.values():
            button.configure(width=MAX_WIDTH, height=35, corner_radius=7, font=CTkFont(DEFAULT_FONT_BOLD, size=16, weight="bold"))

        # FONTS
        h1 = CTkFont(DEFAULT_FONT_BOLD, size=20, weight="bold")
        text = CTkFont(DEFAULT_FONT, size=13, weight="normal")

        obby_frame = CTkFrame(master=main_tab, width=100, height=30)
        obby_frame.grid(row=1, column=0)
        obby_title_label = CTkLabel(master=obby_frame, text="Obby", font=h1).grid(row=1, column=1)

        doObby_check_box = CTkCheckBox(master=obby_frame, text="Do Obby (30% Luck Boost Every 2 Mins)", font=text).grid(row=2, column=1, padx=5, pady=5)
    

from customtkinter import *
from time import sleep
from data.lib import config

CURRENT_VERSION = config.get_current_version()
DEFAULT_FONT = "Segoe UI"
DEFAULT_FONT_BOLD = "Segoe UI Semibold"
MAX_WIDTH = 1000

config_data = config.read()

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
    

from customtkinter import *
from time import sleep
from data.lib import config
import json

CURRENT_VERSION = config.get_current_version()
DEFAULT_FONT = "Segoe UI"
DEFAULT_FONT_BOLD = "Segoe UI Semibold"
MAX_WIDTH = 1000

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.config_data = config.read()
        self.title(f"MACRO NAME v{CURRENT_VERSION}")
        self.geometry("600x300x200x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.tk_var_list = config.generate_tk_list()
        

        set_default_color_theme("blue")

        self.tab_control = CTkTabview(master=self, fg_color=["gray86", "gray17"], height=250)
        
        main_tab = self.tab_control.add("Main")
        crafting_tab = self.tab_control.add("Crafting")
        webhook_tab = self.tab_control.add("Webhook")
        settings_tab = self.tab_control.add("Settings")
        extras_tab = self.tab_control.add("Extras")
        credits_tab = self.tab_control.add("Credits")
        
        self.tab_control.set("Credits")

        self.tab_control.grid(padx=10)

        for button in self.tab_control._segmented_button._buttons_dict.values():
            button.configure(width=MAX_WIDTH, height=35, corner_radius=10, font=CTkFont(DEFAULT_FONT_BOLD, size=16, weight="bold"))
    
        system_button_frame = CTkFrame(master=self)
        system_button_frame.grid(row=1, pady=(5, 8), padx=6, sticky="w")
        start_button = CTkButton(master=system_button_frame, text="Start (F1)", command=self.start, height=30, width=100, corner_radius=4).grid(row=0, column=0, padx=4, pady=4)

        pause_button = CTkButton(master=system_button_frame, text="Pause (F2)", command=self.pause, height=30, width=100, corner_radius=4).grid(row=0, column=1, padx=4, pady=4)

        stop_button = CTkButton(master=system_button_frame, text="Stop (F3)", command=self.stop, height=30, width=100, corner_radius=4).grid(row=0, column=2, padx=4, pady=4)

        self.bind("<F1>", lambda e: self.start())
        self.bind("<F2>", lambda e: self.pause())
        self.bind("<F3>", lambda e: self.stop())

        # FONTS
        h1 = CTkFont(DEFAULT_FONT_BOLD, size=20, weight="bold")
        text = CTkFont(DEFAULT_FONT, size=12, weight="normal")

        obby_frame = CTkFrame(master=main_tab, width=100, height=30, fg_color=["gray81", "gray23"])
        obby_frame.grid(row=0, column=0)
        obby_title_label = CTkLabel(master=obby_frame, text="Obby", font=h1).grid(row=0, column=1)
        do_obby_checkbox = CTkCheckBox(master=obby_frame, text="Do Obby (30% Luck Boost Every 2 Mins)", font=text, variable=self.tk_var_list["do_obby"], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        check_for_obby_buff_check_box = CTkCheckBox(master=obby_frame, text="Check for Obby Buff Effect", font=text, variable=self.tk_var_list["check_for_obby_buff"], onvalue="1", offvalue="0").grid(row=3, column=1, padx=5, pady=5, stick="w")


        auto_equip_frame = CTkFrame(master=main_tab, width=100, height=30, fg_color=["gray81", "gray23"])
        auto_equip_frame.grid(row=0, column=1, stick="ne")
        auto_equip_title = CTkLabel(master=auto_equip_frame, text="Auto Equip", font=h1).grid(row=0)
        enable_auto_equip = CTkCheckBox(master=auto_equip_frame, text="Enable Auto Equip", font=text, variable=self.tk_var_list["enable_auto_equip"], onvalue="1", offvalue="0").grid(row=1)
        auto_equip_aura = CTkEntry(master=auto_equip_frame, placeholder_text="Aura").grid(row=1)
        auto_equip_aura_button = CTkButton(master=auto_equip_frame, text="Submit", command=self.update_auto_equip_aura).grid(row=1, column=1)

        self.theme_var = IntVar(value=1 if self.config_data.get("dark_mode", False) else 2 if self.config_data.get("vibrant_mode", False) else 0)
        customization_label = CTkLabel(master=settings_tab, text="Customization", font=h1)
        customization_label.grid()

        dark_mode_radio = CTkRadioButton(master=settings_tab, text="Dark Mode", variable=self.theme_var, value=1, font=text, command=self.update_theme)
        dark_mode_radio.grid()

        vibrant_mode_radio = CTkRadioButton(master=settings_tab, text="Vibrant Mode", variable=self.theme_var, value=2, command=self.update_theme)
        vibrant_mode_radio.grid()


    def on_close(self):
        config.save_tk_list(self.tk_var_list)
        self.destroy()

    def start(self):
        config.save_tk_list(self.tk_var_list)
    def pause(self):
        config.save_tk_list(self.tk_var_list)
    def stop(self):
        config.save_tk_list(self.tk_var_list)

    def update_auto_equip_aura():
        pass
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

        config.save(self.config_data)

        self.restart_app()  # Restart the app to apply the changes
    
    


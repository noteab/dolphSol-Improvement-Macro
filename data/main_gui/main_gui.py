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
        self.title(f"Radiance Macro v{CURRENT_VERSION}")
        self.geometry("630x315x200x200")
        # self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.tk_var_list = config.generate_tk_list()
        

        set_default_color_theme("blue")
        set_appearance_mode("dark") # NO MORE LIGHT MODE IT IS ABSOLUTELY DOGGY DOO DOO

        self.tab_control = CTkTabview(master=self, fg_color=["gray86", "gray17"], height=265)
        
        main_tab = self.tab_control.add("Main")
        crafting_tab = self.tab_control.add("Crafting")
        discord_tab = self.tab_control.add("Discord")
        merchant_tab = self.tab_control.add("Merchant")
        settings_tab = self.tab_control.add("Settings")
        extras_tab = self.tab_control.add("Extras")
        credits_tab = self.tab_control.add("Credits")

        
        
        self.tab_control.set("Credits")

        self.tab_control.grid(padx=10)

        for button in self.tab_control._segmented_button._buttons_dict.values():
            button.configure(width=MAX_WIDTH, height=35, corner_radius=10, font=CTkFont(DEFAULT_FONT_BOLD, size=15, weight="bold"))
    
        system_button_frame = CTkFrame(master=self)
        system_button_frame.grid(row=1, pady=(5, 8), padx=6, sticky="s")
        start_button = CTkButton(master=system_button_frame, text="Start (F1)", command=self.start, height=30, width=100, corner_radius=4).grid(row=0, column=0, padx=4, pady=4)

        pause_button = CTkButton(master=system_button_frame, text="Pause (F2)", command=self.pause, height=30, width=100, corner_radius=4).grid(row=0, column=1, padx=4, pady=4)

        stop_button = CTkButton(master=system_button_frame, text="Stop (F3)", command=self.stop, height=30, width=100, corner_radius=4).grid(row=0, column=2, padx=4, pady=4)

        self.bind("<F1>", lambda e: self.start())
        self.bind("<F2>", lambda e: self.pause())
        self.bind("<F3>", lambda e: self.stop())

        # FONTS
        h1 = CTkFont(DEFAULT_FONT_BOLD, size=20, weight="bold")
        h2 = CTkFont(DEFAULT_FONT_BOLD, size=15, weight="bold")
        text = CTkFont(DEFAULT_FONT, size=12, weight="normal")

        obby_frame = CTkFrame(master=main_tab, fg_color=["gray81", "gray23"])
        obby_frame.grid(row=0, column=0, sticky="nwe", padx=(1, 1))
        obby_title_label = CTkLabel(master=obby_frame, text="Obby", font=h1).grid(row=0, column=1)
        do_obby_checkbox = CTkCheckBox(master=obby_frame, text="Do Obby (30% Luck Boost Every 2 Mins)", font=text, variable=self.tk_var_list["do_obby"], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        check_for_obby_buff_check_box = CTkCheckBox(master=obby_frame, text="Check for Obby Buff Effect", font=text, variable=self.tk_var_list["check_for_obby_buff"], onvalue="1", offvalue="0").grid(row=3, column=1, padx=5, pady=5, stick="w")

        auto_equip_frame = CTkFrame(master=main_tab, width=200, height=30, fg_color=["gray81", "gray23"])
        auto_equip_frame.grid(row=0, column=1, stick="ne", padx=(5, 0))
        auto_equip_title = CTkLabel(master=auto_equip_frame, text="Auto Equip", font=h1).grid(row=0, pady=(0, 3), columnspan=2)

        enable_auto_equip = CTkCheckBox(master=auto_equip_frame, text="Enable Auto Equip", font=text, variable=self.tk_var_list["enable_auto_equip"], onvalue="1", offvalue="0").grid(row=1, pady=(1, 6), sticky="w", padx=(5, 4))
        self.auto_equip_aura = CTkEntry(master=auto_equip_frame, placeholder_text="Aura", width=272)
        self.auto_equip_aura.grid(row=2, padx=(5, 0), sticky="e")
        auto_equip_aura_button = CTkButton(master=auto_equip_frame, text="Submit", command=self.update_auto_equip_aura, width=50).grid(row=2, column=1, padx=(4, 6), pady=(0,6), sticky="e")


        item_collection_frame = CTkFrame(master=main_tab, fg_color=["gray81", "gray23"])
        item_collection_frame.grid(row=1, pady=(6, 0), sticky="we", columnspan=2, column=0, padx=(1, 0))
        
        item_collection_title = CTkLabel(master=item_collection_frame, text="Collect Items", font=h1).grid(row=0, padx=5, columnspan=2)

        enable_collect_items = CTkCheckBox(master=item_collection_frame, text="Enable Item Collection", font=text, variable=self.tk_var_list["collect_items"], onvalue="1", offvalue="0").grid(row=1, sticky="w", padx=5, pady=5)
        fps_30_patch = CTkCheckBox(master=item_collection_frame, text="30 FPS Path", font=text, variable=self.tk_var_list["30_fps_path"], onvalue="1", offvalue="0").grid(row=2, sticky="w", padx=5, pady=5)
        
        spot_collection_frame = CTkFrame(master=item_collection_frame, fg_color=["gray65", "gray28"])
        collect_item_spots_title = CTkLabel(master=spot_collection_frame, text="Collect Item Spots", font=h2).grid(row=0, padx=5, column=0, columnspan=8)
        spot_collection_frame.grid(row=1, sticky="we", column=1, padx=(64, 1), pady=(5, 7), rowspan=2, ipady=5, ipadx=1)

        CTkCheckBox(master=spot_collection_frame, text='1', width=45, variable=self.tk_var_list['collect_spot_1'], onvalue='1', offvalue='0').grid(row=1, column=0, sticky='e', padx=(5, 0))
        for i in range(1, 8):
            exec(f"CTkCheckBox(master=spot_collection_frame, text='{i + 1}', width=45, variable=self.tk_var_list['collect_spot_{i + 1}'], onvalue='1', offvalue='0').grid(row=1, column={i}, sticky='e')")

        self.theme_var = IntVar(value=1 if self.config_data.get("dark_mode", False) else 2 if self.config_data.get("vibrant_mode", False) else 0)
        customization_label = CTkLabel(master=settings_tab, text="Customization", font=h1)
        customization_label.grid()


        item_crafting_frame = CTkFrame(master=crafting_tab, fg_color=["gray81", "gray23"])
        item_crafting_frame.grid(row=0, column=0, padx=(1, 0))
        item_crafting_title = CTkLabel(master=item_crafting_frame, text="Automatic Item Crafting", font=h1).grid(row=0, padx=5)
        enable_item_crafting_checkbox = CTkCheckBox(master=item_crafting_frame, text="Enable Automatic Item Crafting", font=text, variable=self.tk_var_list["automatic_item_crafting"], onvalue='1', offvalue='0').grid(row=1, padx=5, pady=5, sticky="w")
        item_crafting_settings_button = CTkButton(master=item_crafting_frame, text="Automatic Item Crafting Settings", command=self.open_automatic_item_crafting_settings, width=286, font=text).grid(padx=5, pady=5)

        potion_crafting_frame = CTkFrame(master=crafting_tab, fg_color=["gray81", "gray23"])
        potion_crafting_frame.grid(row=0, column=1, padx=(6, 5), sticky="n")
        potion_crafting_title = CTkLabel(master=potion_crafting_frame, text="Automatic Potion Crafting", font=h1).grid(row=0, padx=5)
        enable_potion_crafting_checkbox = CTkCheckBox(master=potion_crafting_frame, text="Enable Automatic Potion Crafting", font=text, variable=self.tk_var_list["automatic_potion_crafting"], onvalue='1', offvalue='0').grid(row=1, padx=5, pady=5, sticky="w")
        potion_crafting_settings_button = CTkButton(master=potion_crafting_frame, text="Automatic Potion Crafting Settings", width=284, command=self.open_automatic_potion_crafting_settings).grid(row=2, padx=5, pady=5)

        cycle_auto_add_settings_frame = CTkFrame(master=crafting_tab, fg_color=["gray81", "gray23"])
        cycle_auto_add_settings_frame.grid(row=1, columnspan=2, sticky="w", pady=(6, 0), padx=(1, 0))
        switch_auto_add_title = CTkLabel(master=cycle_auto_add_settings_frame, text='Cycle "Auto Add"', font=h1).grid(row=0)
        enable_switch_auto_add_checkbox = CTkCheckBox(master=cycle_auto_add_settings_frame, text='Enable Cycle "Auto Add" (For both Potion Crafting and Item Crafting)', variable=self.tk_var_list["cycle_auto_add"], onvalue="1", offvalue="0", font=text).grid(row=1, padx=5, sticky="w", pady=5)
        cycle_auto_add_settings = CTkButton(master=cycle_auto_add_settings_frame, text="Cycle Auto Add Settings", font=text, command=self.open_automatic_potion_crafting_settings, width=586).grid(row=2, padx=5, pady=5)

        discord_webhook_frame = CTkFrame(master=discord_tab, fg_color=["gray81", "gray23"])
        discord_webhook_frame.grid(row=0, column=0, sticky="n", pady=(0, 0), padx=(1, 0))
        discord_webhook_title = CTkLabel(master=discord_webhook_frame, text="Discord Webhooks", font=h1).grid(row=0, padx=5)
        enable_discord_webhook = CTkCheckBox(master=discord_webhook_frame, text="Enable Discord Webhooks", font=text, variable=self.tk_var_list['discord_webhook'], onvalue="1", offvalue="0").grid(row=1, padx=5, pady=5, sticky="w")
        discord_webhook_list = CTkButton(master=discord_webhook_frame, text="Add Discord Webhook", font=text, command=self.open_add_discord_webhook, width=286).grid(row=2, padx=5, pady=5)
        discord_webhook_settings = CTkButton(master=discord_webhook_frame, text="Discord Webhook Settings", font=text, command=self.open_discord_webhook_settings, width=286).grid(row=3, padx=5, pady=5)
        
        discord_bot_frame = CTkFrame(master=discord_tab, fg_color=["gray81", "gray23"])
        discord_bot_frame.grid(row=0, column=1, sticky="n", pady=(0, 0), padx=(6, 0))
        discord_bot_title = CTkLabel(master=discord_bot_frame, text="Discord Bot", font=h1).grid(row=0, padx=5)
        enable_discord_bot = CTkCheckBox(master=discord_bot_frame, text="Enable Discord Bot", font=text, variable=self.tk_var_list["discord_bot"], onvalue="1", offvalue="0").grid(row=1, padx=5, pady=5, sticky="w")
        add_discord_bot_button = CTkButton(master=discord_bot_frame, text="Add Discord Bot", font=text, command=self.open_add_discord_bot, width=285).grid(row=2, padx=5, pady=5)
        discord_bot_settings_button = CTkButton(master=discord_bot_frame, text="Discord Bot Settings", font=text, command=self.open_discord_bot_settings, width=285).grid(row=3, padx=5, pady=5)

        community_frame = CTkFrame(master=discord_tab, fg_color=["gray81", "gray23"])
        community_frame.grid(row=1, columnspan=2, pady=(6, 0), padx=(1, 0), sticky="n")
        community_title = CTkLabel(master=community_frame, text="Community", font=h1, width=586).grid(row=0, padx=5)
        coming_soon = CTkLabel(master=community_frame, text="Website Coming Soon", font=text, width=586).grid(row=1, padx=5, pady=(3, 5))

        jester_frame = CTkFrame(master=merchant_tab, fg_color=["gray81", "gray23"])
        jester_frame.grid(row=0, column=0, sticky="n", padx=(1, 0))
        jester_title = CTkLabel(master=jester_frame, text="Jester Autobuy", font=h1).grid(row=0, padx=5)
        enable_jester_autobuy = CTkCheckBox(master=jester_frame, text="Enable Jester Autobuy", font=text, variable=self.tk_var_list['jester_autobuy'], onvalue="1", offvalue="0").grid(row=1, pady=5, padx=5, sticky="w")
        jester_item_settings = CTkButton(master=jester_frame, text="Jester Item Settings", font=text, command=self.open_jester_autobuy_settings, width=286).grid(row=3, padx=5, pady=(0, 5))
        
        mari_frame = CTkFrame(master=merchant_tab, fg_color=["gray81", "gray23"])
        mari_frame.grid(row=0, column=1, sticky="n", padx=(6, 0))
        mari_title = CTkLabel(master=mari_frame, text="Mari Autobuy", font=h1).grid(row=0, padx=5)
        enable_mari_autobuy = CTkCheckBox(master=mari_frame, text="Enable Mari Autobuy", font=text, variable=self.tk_var_list['mari_autobuy'], onvalue="1", offvalue="0").grid(row=1, pady=5, padx=5, sticky="w")
        mari_autobuy_settings = CTkButton(master=mari_frame, text="Mari Item Settings", font=text, command=self.open_mari_autobuy_settings, width=286).grid(row=3, padx=5, pady=(0, 5))

        jester_exchange_frame = CTkFrame(master=merchant_tab, fg_color=["gray81", "gray23"])
        jester_exchange_frame.grid(row=1, columnspan=2, sticky="w", pady=(5, 0), padx=(1, 0))
        jester_exchance_title = CTkLabel(master=jester_exchange_frame, text="Jester Exchange", font=h1).grid(row=0, padx=5)

        vibrant_mode_radio = CTkRadioButton(master=settings_tab, text="Vibrant Mode", variable=self.theme_var, value=2, command=self.update_theme).grid(row=2)


    def on_close(self):
        config.save_tk_list(self.tk_var_list)
        self.destroy()

    def start(self):
        config.save_tk_list(self.tk_var_list)
    def pause(self):
        config.save_tk_list(self.tk_var_list)
    def stop(self):
        config.save_tk_list(self.tk_var_list)

    def open_jester_autobuy_settings(self):
        from merchant import jester_autobuy_gui

    def open_mari_autobuy_settings(self):
        from merchant import mari_autobuy_gui

    def open_discord_bot_settings(self):
        from data.discord_bot import discord_bot_gui
    
    def open_add_discord_bot(self):
        from data.discord_bot import discord_bot_gui
        # run discord bot

    def open_discord_webhook_settings(self):
        from data.discord_webhook import discord_webhook_gui
        # run discord webhook settings

    def open_add_discord_webhook(self):
        from data.discord_webhook import discord_webhook_gui
        #run discord webhook gui

    def open_cycle_auto_add_settings(self):
        from data.cycle_auto_add import cycle_auto_add_gui
        # Run cycle_auto_add_gui

    def open_automatic_potion_crafting_settings(self):
        from data.potion_crafting import potion_crafting_gui
        # Run potion_crafting_gui

    def open_automatic_item_crafting_settings(self):
        from data.item_crafting import item_crafting_gui
        # Run item_crafting_gui

    def update_auto_equip_aura(self):
        self.config_data["auto_equip_aura"] = self.auto_equip_aura.get()
        config.save(self.config_data)


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
    
    


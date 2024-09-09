import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
import sys
import threading
import time
import keyboard
import pystray
from PIL import Image, ImageDraw

# Print "PLEASE WAIT..." immediately
def print_please_wait():
    print("PLEASE WAIT...")
    sys.stdout.flush()

# Call the function right at the start of the script
print_please_wait()

# Constants
CONFIG_FILE = "../config.json"

# Default search paths for the scripts
DEFAULT_MERCHANT_PATH = "dolphSol-Improvement-Macro-Noteab-Improvement/Python_Support/Merchant Feature/Main_Merchant.py"
DEFAULT_DISCORD_PATH = "dolphSol-Improvement-Macro-Noteab-Improvement/Python_Support/Installation/discord_cmd.py"

# Load configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "auto_run_merchant": False,
        "auto_run_discord": False,
        "merchant_hotkey": "",
        "discord_hotkey": "",
        "merchant_script_path": "",
        "discord_cmd_path": ""
    }

# Save configuration to file
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Function to automatically search for the script paths
def auto_find_script(script_name):
    for root, dirs, files in os.walk(os.path.expanduser("~")):  # Search starting from the home directory
        if script_name in files:
            return os.path.join(root, script_name)
    return None

# Function to run Merchant Feature script
def run_merchant():
    config = load_config()
    script_path = config.get("merchant_script_path", "")
    if script_path and os.path.exists(script_path):
        print("Running Merchant script...")
        subprocess.Popen([sys.executable, script_path])
    else:
        messagebox.showerror("Error", "Merchant script not found. Please set the path in the 'SET PATH' tab.")
        print("Merchant script not found.")

# Function to run Discord bot script
def run_discord_bot():
    config = load_config()
    script_path = config.get("discord_cmd_path", "")
    if script_path and os.path.exists(script_path):
        print("Running Discord bot script...")
        subprocess.Popen([sys.executable, script_path])
    else:
        messagebox.showerror("Error", "Discord bot script not found. Please set the path in the 'SET PATH' tab.")
        print("Discord bot script not found.")

# Hotkey detection and action
def hotkey_listener():
    while True:
        config = load_config()  # Reload config each time to pick up updates
        merchant_hotkey = config.get("merchant_hotkey", "")
        discord_hotkey = config.get("discord_hotkey", "")

        if merchant_hotkey and keyboard.is_pressed(merchant_hotkey):
            print(f"Detected hotkey {merchant_hotkey} for Merchant.")
            run_merchant()

        if discord_hotkey and keyboard.is_pressed(discord_hotkey):
            print(f"Detected hotkey {discord_hotkey} for Discord bot.")
            run_discord_bot()

        time.sleep(0.1)  # Prevent high CPU usage

# Minimize to tray
def on_quit(icon, item):
    icon.stop()
    root.destroy()

def create_image():
    # Generate an image for the system tray icon
    image = Image.new('RGB', (64, 64), (0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
    return image

def on_icon_click(icon, item):
    root.deiconify()  # Restore the window
    root.update_idletasks()

# Create the system tray icon
icon = pystray.Icon("name", create_image(), "listener for autorun feature")
icon.menu = pystray.Menu(
    pystray.MenuItem('Restore', on_icon_click),
    pystray.MenuItem('Quit', on_quit)
)

# GUI application
class App:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.setup_ui()
        self.check_and_prompt_paths()  # Check if paths are set, otherwise prompt
        threading.Thread(target=hotkey_listener, daemon=True).start()

    def setup_ui(self):
        self.root.title("Settings")
        self.tab_control = ttk.Notebook(self.root)

        # Settings Tab
        self.settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.settings_tab, text="Settings")
        self.setup_settings_tab()

        # Set Path Tab
        self.set_path_tab = ttk.Frame(self.tab_control)
        # self.tab_control.add(self.set_path_tab, text="SET PATH")
        # self.setup_set_path_tab()
        self.config["merchant_script_path"] = "../Merchant Feature/Merchant_Setting_GUI.pyw"
        self.config["discord_cmd_path"] = "../discord_cmd.py"

        save_config(self.config)

        self.tab_control.pack(expand=1, fill="both")

    def setup_settings_tab(self):
        self.auto_run_merchant_var = tk.BooleanVar(value=self.config["auto_run_merchant"])
        self.auto_run_discord_var = tk.BooleanVar(value=self.config["auto_run_discord"])

        tk.Checkbutton(self.settings_tab, text="Auto Run Merchant Function", variable=self.auto_run_merchant_var).pack()
        tk.Checkbutton(self.settings_tab, text="Auto Run Discord Bot", variable=self.auto_run_discord_var).pack()

        tk.Label(self.settings_tab, text="Merchant Hotkey:").pack()
        self.merchant_hotkey_entry = tk.Entry(self.settings_tab)
        self.merchant_hotkey_entry.insert(0, self.config["merchant_hotkey"])
        self.merchant_hotkey_entry.pack()

        tk.Label(self.settings_tab, text="Discord Bot Hotkey:").pack()
        self.discord_hotkey_entry = tk.Entry(self.settings_tab)
        self.discord_hotkey_entry.insert(0, self.config["discord_hotkey"])
        self.discord_hotkey_entry.pack()

        tk.Button(self.settings_tab, text="Save Config", command=self.save_config).pack()

    # def setup_set_path_tab(self):
    #     tk.Label(self.set_path_tab, text="Merchant Script Path:").pack()
    #     self.merchant_path_entry = tk.Entry(self.set_path_tab)
    #     self.merchant_path_entry.insert(0, self.config.get("merchant_script_path", ""))
    #     self.merchant_path_entry.pack()
    #     tk.Button(self.set_path_tab, text="Browse", command=self.set_merchant_path).pack()

    #     tk.Label(self.set_path_tab, text="Discord Cmd Script Path:").pack()
    #     self.discord_path_entry = tk.Entry(self.set_path_tab)
    #     self.discord_path_entry.insert(0, self.config.get("discord_cmd_path", ""))
    #     self.discord_path_entry.pack()
    #     tk.Button(self.set_path_tab, text="Browse", command=self.set_discord_path).pack()

    # def set_merchant_path(self):
    #     path = filedialog.askopenfilename(title="Select Merchant Script", filetypes=[("Python Files", "*.py")])
    #     if path:
    #         self.merchant_path_entry.delete(0, tk.END)
    #         self.merchant_path_entry.insert(0, path)
    #         self.config["merchant_script_path"] = path
    #         save_config(self.config)

    # def set_discord_path(self):
    #     path = filedialog.askopenfilename(title="Select Discord Cmd Script", filetypes=[("Python Files", "*.py")])
    #     if path:
    #         self.discord_path_entry.delete(0, tk.END)
    #         self.discord_path_entry.insert(0, path)
    #         self.config["discord_cmd_path"] = path
    #         save_config(self.config)

    def save_config(self):
        self.config["auto_run_merchant"] = self.auto_run_merchant_var.get()
        self.config["auto_run_discord"] = self.auto_run_discord_var.get()
        self.config["merchant_hotkey"] = self.merchant_hotkey_entry.get()
        self.config["discord_hotkey"] = self.discord_hotkey_entry.get()

        save_config(self.config)
        messagebox.showinfo("Info", "Configuration saved")

    def check_and_prompt_paths(self):
        """Check if paths are set, otherwise try to find them or prompt user."""
        config = load_config()

        # Check and find the merchant script
        if not config.get("merchant_script_path"):
            found_merchant = auto_find_script("Main_Merchant.py")
            if found_merchant:
                config["merchant_script_path"] = found_merchant
                save_config(config)
            else:
                messagebox.showinfo("Info", "Please set the path for the Merchant script in the 'SET PATH' tab.")
                self.tab_control.select(self.set_path_tab)

        # Check and find the discord_cmd script
        if not config.get("discord_cmd_path"):
            found_discord = auto_find_script("discord_cmd.py")
            if found_discord:
                config["discord_cmd_path"] = found_discord
                save_config(config)
            else:
                messagebox.showinfo("Info", "Please set the path for the Discord script in the 'SET PATH' tab.")
                self.tab_control.select(self.set_path_tab)

# Add a function to show "DO NOT CLOSE THIS TERMINAL" message when minimized
def minimize_to_tray():
    root.withdraw()
    print("KEEP THIS TERMINAL OPEN IF YOU WANT THE FUNCTION TO WORK!!!")  # Message to show in terminal

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", minimize_to_tray)  # Show message and minimize to tray
    app = App(root)

    # Start the tray icon
    icon.run_detached()
    
    # Start the Tkinter main loop
    root.mainloop()

import tkinter as tk
from tkinter import messagebox
import json
import os
import subprocess
import sys
import threading
import time
import keyboard
import pystray
from PIL import Image, ImageDraw
import psutil

# Constants
CONFIG_FILE = "config.json"

# Load configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "auto_run_merchant": False,
        "auto_run_discord": False,
        "merchant_hotkey": "",
        "discord_hotkey": ""
    }

# Save configuration to file
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Function to run Merchant Feature script
def run_merchant():
    script_path = os.path.join(os.path.dirname(__file__), "Main_Merchant.py")
    if os.path.exists(script_path):
        print("Running Merchant script...")
        subprocess.Popen([sys.executable, script_path])
    else:
        messagebox.showerror("Error", "Merchant script not found.")
        print("Merchant script not found.")

# Function to run Discord bot script
def run_discord_bot():
    support_dir = os.path.join(os.path.dirname(__file__), "Python_Support")
    found = False

    for root, dirs, files in os.walk(support_dir):
        if "discord_cmd.py" in files:
            script_path = os.path.join(root, "discord_cmd.py")
            print("Running Discord bot script...")
            subprocess.Popen([sys.executable, script_path])
            found = True
            break
    
    if not found:
        messagebox.showerror("Error", "Discord bot script not found.")
        print("Discord bot script not found.")

# Hotkey detection and action
def hotkey_listener():
    config = load_config()
    while True:
        if config["auto_run_merchant"]:
            if keyboard.is_pressed(config["merchant_hotkey"]):
                print(f"Detected hotkey {config['merchant_hotkey']} for Merchant.")
                run_merchant()
        if config["auto_run_discord"]:
            if keyboard.is_pressed(config["discord_hotkey"]):
                print(f"Detected hotkey {config['discord_hotkey']} for Discord bot.")
                run_discord_bot()
        time.sleep(0.1)  # Reduce CPU usage

# Check if a process is running
def is_process_running(name):
    name = name.lower()
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == name:
            return True
    return False

# Minimize to tray
def on_quit(icon, item):
    icon.stop()
    root.destroy()

def create_image():
    # Generate an image for the system tray icon
    image = Image.new('RGB', (64, 64), (0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (16, 16, 48, 48),
        fill=(255, 255, 255))
    return image

def on_icon_click(icon, item):
    root.deiconify()  # Restore the window
    root.update_idletasks()

# Create the system tray icon
icon = pystray.Icon("name", create_image(), "App Name")
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
        threading.Thread(target=hotkey_listener, daemon=True).start()

    def setup_ui(self):
        self.root.title("Settings")

        self.auto_run_merchant_var = tk.BooleanVar(value=self.config["auto_run_merchant"])
        self.auto_run_discord_var = tk.BooleanVar(value=self.config["auto_run_discord"])

        tk.Checkbutton(self.root, text="Auto Run Merchant Function", variable=self.auto_run_merchant_var).pack()
        tk.Checkbutton(self.root, text="Auto Run Discord Bot", variable=self.auto_run_discord_var).pack()

        tk.Label(self.root, text="Merchant Hotkey:").pack()
        self.merchant_hotkey_entry = tk.Entry(self.root)
        self.merchant_hotkey_entry.insert(0, self.config["merchant_hotkey"])
        self.merchant_hotkey_entry.pack()

        tk.Label(self.root, text="Discord Bot Hotkey:").pack()
        self.discord_hotkey_entry = tk.Entry(self.root)
        self.discord_hotkey_entry.insert(0, self.config["discord_hotkey"])
        self.discord_hotkey_entry.pack()

        tk.Button(self.root, text="Save Config", command=self.save_config).pack()

    def save_config(self):
        self.config["auto_run_merchant"] = self.auto_run_merchant_var.get()
        self.config["auto_run_discord"] = self.auto_run_discord_var.get()
        self.config["merchant_hotkey"] = self.merchant_hotkey_entry.get()
        self.config["discord_hotkey"] = self.discord_hotkey_entry.get()
        save_config(self.config)
        messagebox.showinfo("Info", "Configuration saved")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: root.withdraw())  # Minimize to tray
    app = App(root)

    # Start the tray icon
    icon.run_detached()
    
    # Start the Tkinter main loop
    root.mainloop()

import tkinter as tk
from tkinter import ttk
from tkinter import BooleanVar, filedialog, messagebox
from tkinter import BooleanVar
import json
from pathlib import Path
from dotenv import load_dotenv, set_key
import os
import cv2
import numpy as np
import pyautogui
from tkinter import Toplevel
from PIL import ImageGrab



# Set up the paths
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE_PATH = BASE_DIR / 'config.json'
ENV_FILE_PATH = BASE_DIR / '.env'

# Load the .env file
load_dotenv(dotenv_path=ENV_FILE_PATH)

# Load the config.json file
def load_config():
    if CONFIG_FILE_PATH.exists():
        with open(CONFIG_FILE_PATH, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_config():
    with open(CONFIG_FILE_PATH, 'w') as file:
        json.dump(config, file, indent=4)
        
# Function to import a previous config file
def import_config():
    file_path = filedialog.askopenfilename(
        title="Select a Config File",
        filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
    )
    if file_path:
        try:
            with open(file_path, 'r') as file:
                new_config = json.load(file)
                config.update(new_config)
                save_config()  # Save the imported config to the existing config.json
                messagebox.showinfo("Success", "Configuration imported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load the config file.\n{e}")
            
config = load_config()

# Toggle Auto-reconnect:
def toggle_reconnect():
    enable = reconnect_var.get()
    config['enable_reconnect'] = enable
    save_config()

# Save the private server link and extract the code
def save_private_server_link():
    link = private_server_link_var.get()
    config['private_server_link'] = link
    
    # Extract the private server code from the link
    try:
        code = link.split('privateServerLinkCode=')[1]
        config['private_server_code'] = code
        save_config()
        print(f"Private server code extracted: {code}")
    except IndexError:
        messagebox.showerror("Error", f"Invalid link format. Please ensure the link contains 'privateServerLinkCode=' by convert a sharelink code to privateServerLinkCode!")

# Toggle Auto Item Add
def toggle_auto_item_add():
    enable = auto_item_add_var.get()
    config['enable_auto_item_crafting'] = enable
    save_config()

# Update Slot Option
def update_slot_option(slot, value):
    config[f'slot_{slot}'] = value
    save_config()

# Update Crafting Interval
def update_craft_interval(interval):
    config['crafting_interval'] = interval
    save_config()
    print(f"Crafting Interval set to: {interval} minute(s)")
    
# Function to update the selected item in the config for Mari
def update_mari_item(slot, value):
    config[f'mari_slot_{slot}'] = value
    save_config()

# Function to update the selected item in the config for Jester
def update_jester_item(slot, value):
    config[f'jester_slot_{slot}'] = value
    save_config()
    
# Function to update and save the amount for Mari items
def update_mari_amount(slot, amount):
    config[f'mari_amount_{slot}'] = amount
    save_config()

# Function to update and save the amount for Jester items
def update_jester_amount(slot, amount):
    config[f'jester_amount_{slot}'] = amount
    save_config()

# Save auto merchant option
def save_auto_buy_setting():
    config['enable_auto_merchant'] = auto_buy_var.get()
    save_config()
    
# Update Bot Info in .env
def update_bot_info():
    set_key(ENV_FILE_PATH, 'DISCORD_BOT_TOKEN', bot_token_var.get())
    set_key(ENV_FILE_PATH, 'DISCORD_CHANNEL_ID', channel_id_var.get())
    set_key(ENV_FILE_PATH, 'YOUR_DISCORD_USER_ID', user_id_var.get())


# Toggle Auto Biome
def toggle_auto_biome():
    enable = auto_biome_var.get()
    config['is_auto_biome'] = enable
    save_config()
    
    
# Update Biome Region
def update_biome_region():
    x, y, w, h = biome_x_var.get(), biome_y_var.get(), biome_width_var.get(), biome_height_var.get()
    config['BIOME_OCR_TEXT_REGION'] = [x, y, w, h]
    save_config()
    display_bounding_box()

# Display Bounding Box with scaling
def display_bounding_box(scaling_factor=0.85):
    # Clear previous bounding box by refreshing the screen
    cv2.destroyAllWindows()

    region = config['BIOME_OCR_TEXT_REGION']
    x, y, w, h = region

    # Capture the current screen
    screen = np.array(pyautogui.screenshot())
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

    # Draw the bounding box on the original screen size
    cv2.rectangle(screen, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Resize the screen to the desired scale for display
    screen_resized = cv2.resize(screen, (0, 0), fx=scaling_factor, fy=scaling_factor)

    # Calculate the scaled positions for the bounding box
    x_scaled = int(x * scaling_factor)
    y_scaled = int(y * scaling_factor)
    w_scaled = int(w * scaling_factor)
    h_scaled = int(h * scaling_factor)

    # Draw the scaled bounding box on the resized screen
    cv2.rectangle(screen_resized, (x_scaled, y_scaled), (x_scaled + w_scaled, y_scaled + h_scaled), (0, 255, 0), 2)

    # Show the resized screen with the bounding box
    cv2.imshow('Biome OCR Region (Scaled)', screen_resized)
    cv2.waitKey(1)

# Initialize main window
root = tk.Tk()
root.title("Python DolphSol SETTING (Noteab)")
root.geometry("750x380")

# Create notebook (tabs)
notebook = ttk.Notebook(root)

# Main tab
main_tab = ttk.Frame(notebook, width=350, height=350)
main_tab.pack_propagate(False)
notebook.add(main_tab, text="< Main >")

# Setting tab
setting_tab = ttk.Frame(notebook, width=350, height=350)
setting_tab.pack_propagate(False)
notebook.add(setting_tab, text="< Settings >")


# Biome setting tab
biome_tab = ttk.Frame(notebook, width=350, height=350)
biome_tab.pack_propagate(False)
notebook.add(biome_tab, text="< Biomes >")

# Reconnect Private Server tab
reconnect_tab = ttk.Frame(notebook, width=350, height=350)
reconnect_tab.pack_propagate(False)
notebook.add(reconnect_tab, text="< Reconnect PS >")

# NPC/Merchant Tab
merchant_tab = ttk.Frame(notebook, width=350, height=350)
reconnect_tab.pack_propagate(False)
notebook.add(merchant_tab, text="< Merchant/NPC Auto Buy>")

# Bot setting tab
bot_tab = ttk.Frame(notebook, width=350, height=350)
bot_tab.pack_propagate(False)
notebook.add(bot_tab, text="< Bot >")


# Auto Biome Section (Merged with Biome OCR Region)
auto_biome_frame = ttk.Labelframe(biome_tab, text="Auto Biome & Biome OCR Region")
auto_biome_frame.pack(fill="x", padx=10, pady=5)

auto_biome_var = tk.BooleanVar(value=config.get('is_auto_biome', False))
enable_auto_biome = ttk.Checkbutton(auto_biome_frame, text="Enable Auto Biome Detection", variable=auto_biome_var, command=toggle_auto_biome)
enable_auto_biome.grid(row=0, column=0, sticky="w", padx=5, pady=5)

# Biome OCR Region Sliders with manual entry and increased slider length
biome_x_var = tk.IntVar(value=config['BIOME_OCR_TEXT_REGION'][0])
biome_y_var = tk.IntVar(value=config['BIOME_OCR_TEXT_REGION'][1])
biome_width_var = tk.IntVar(value=config['BIOME_OCR_TEXT_REGION'][2])
biome_height_var = tk.IntVar(value=config['BIOME_OCR_TEXT_REGION'][3])

def update_biome_x(val):
    biome_x_var.set(int(float(val)))  # Convert to float first, then to int
    update_biome_region()

def update_biome_y(val):
    biome_y_var.set(int(float(val)))  # Convert to float first, then to int
    update_biome_region()

def update_biome_width(val):
    biome_width_var.set(int(float(val)))  # Convert to float first, then to int
    update_biome_region()

def update_biome_height(val):
    biome_height_var.set(int(float(val)))  # Convert to float first, then to int
    update_biome_region()

# Biome X Region
ttk.Label(auto_biome_frame, text="Biome X Region:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
x_slider = tk.Scale(auto_biome_frame, from_=0, to_=5000, orient="horizontal", variable=biome_x_var, command=update_biome_x, resolution=0.1, length=400)
x_slider.grid(row=1, column=1, padx=5, pady=2)
x_entry = ttk.Entry(auto_biome_frame, textvariable=biome_x_var, width=6)
x_entry.grid(row=1, column=2, padx=5, pady=2)
x_entry.bind("<Return>", lambda event: update_biome_x(x_entry.get()))

# Biome Y Region
ttk.Label(auto_biome_frame, text="Biome Y Region:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
y_slider = tk.Scale(auto_biome_frame, from_=0, to_=5000, orient="horizontal", variable=biome_y_var, command=update_biome_y, resolution=0.1, length=400)
y_slider.grid(row=2, column=1, padx=5, pady=2)
y_entry = ttk.Entry(auto_biome_frame, textvariable=biome_y_var, width=6)
y_entry.grid(row=2, column=2, padx=5, pady=2)
y_entry.bind("<Return>", lambda event: update_biome_y(y_entry.get()))

# Biome Width Region
ttk.Label(auto_biome_frame, text="Biome Region Width:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
width_slider = tk.Scale(auto_biome_frame, from_=0, to_=5000, orient="horizontal", variable=biome_width_var, command=update_biome_width, resolution=0.1, length=400)
width_slider.grid(row=3, column=1, padx=5, pady=2)
width_entry = ttk.Entry(auto_biome_frame, textvariable=biome_width_var, width=6)
width_entry.grid(row=3, column=2, padx=5, pady=2)
width_entry.bind("<Return>", lambda event: update_biome_width(width_entry.get()))

# Biome Height Region
ttk.Label(auto_biome_frame, text="Biome Height Region:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
height_slider = tk.Scale(auto_biome_frame, from_=0, to_=5080, orient="horizontal", variable=biome_height_var, command=update_biome_height, resolution=0.1, length=400)
height_slider.grid(row=4, column=1, padx=5, pady=2)
height_entry = ttk.Entry(auto_biome_frame, textvariable=biome_height_var, width=6)
height_entry.grid(row=4, column=2, padx=5, pady=2)
height_entry.bind("<Return>", lambda event: update_biome_height(height_entry.get()))

# Auto Item Add Section
auto_item_add_var = tk.BooleanVar(value=config.get('enable_auto_item_crafting', False))
auto_item_add_frame = ttk.Labelframe(main_tab, text="Auto Item Crafting (Replicated from original method DolphSol)")
auto_item_add_frame.pack(fill="x", padx=10, pady=5)

enable_auto_item_add = ttk.Checkbutton(auto_item_add_frame, text="Enable Auto Crafting ?", variable=auto_item_add_var, command=toggle_auto_item_add)
enable_auto_item_add.grid(row=0, column=0, sticky="w", padx=5, pady=5)

# Crafting Slots
slots_frame = ttk.Labelframe(auto_item_add_frame, text="Crafting Slots")
slots_frame.grid(row=1, column=0, padx=5, pady=5)

# Dropdowns for each slot
slot_options = [item['Item_Name'] for item in config.get('item_crafting_choices', [])]

slot_vars = [tk.StringVar(value=config.get(f'slot_{i+1}', "None")) for i in range(3)]
for i in range(3):
    ttk.Label(slots_frame, text=f"Slot {i+1}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
    
    combobox = ttk.Combobox(slots_frame, textvariable=slot_vars[i], values=slot_options, state="readonly", width=20)
    combobox.grid(row=i, column=1, padx=5, pady=2)
    
    # Bind the selection event to update the config when a new item is selected
    combobox.bind('<<ComboboxSelected>>', lambda event, i=i: update_slot_option(i+1, slot_vars[i].get()))

# Crafting Interval
craft_interval_var = tk.StringVar(value=config.get('crafting_interval', "1"))
ttk.Label(auto_item_add_frame, text="Crafting Interval (minutes):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
craft_interval_spinbox = ttk.Spinbox(auto_item_add_frame, from_=1, to_=60, textvariable=craft_interval_var, width=5, command=lambda: update_craft_interval(craft_interval_var.get()))
craft_interval_spinbox.grid(row=2, column=1, sticky="w", padx=5, pady=5)

# Initialize the reconnect variable
reconnect_var = BooleanVar(value=config.get('enable_reconnect', False))

# Add Reconnect Checkbox and Private Server Link Section
reconnect_frame = ttk.Labelframe(reconnect_tab, text="Reconnect Options")
reconnect_frame.pack(fill="x", padx=10, pady=5)

enable_reconnect = ttk.Checkbutton(reconnect_frame, text="Enable Auto-Reconnect", variable=reconnect_var, command=toggle_reconnect)
enable_reconnect.grid(row=0, column=0, sticky="w", padx=5, pady=5)

# Private Server Link input
private_server_link_var = tk.StringVar(value=config.get('private_server_link', ''))
ttk.Label(reconnect_frame, text="Private Server Link:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
private_server_link_entry = ttk.Entry(reconnect_frame, textvariable=private_server_link_var, width=50)
private_server_link_entry.grid(row=1, column=1, padx=5, pady=5)

# Add a button to save the link
save_link_button = ttk.Button(reconnect_frame, text="Save Ps Link", command=save_private_server_link)
save_link_button.grid(row=2, column=0, columnspan=2, pady=10)


# MERCHANT MAIN Section #

# Merchant OCR Region
merchant_x_var = tk.IntVar(value=config.get('MERCHANT_OCR_TEXT_REGION', [0, 0, 0, 0])[0])
merchant_y_var = tk.IntVar(value=config.get('MERCHANT_OCR_TEXT_REGION', [0, 0, 0, 0])[1])
merchant_width_var = tk.IntVar(value=config.get('MERCHANT_OCR_TEXT_REGION', [0, 0, 0, 0])[2])
merchant_height_var = tk.IntVar(value=config.get('MERCHANT_OCR_TEXT_REGION', [0, 0, 0, 0])[3])

merchant_detection_method_var = tk.StringVar(value=config.get('merchant_detection_method', 'name'))

# merchant detection method
def update_merchant_detection_method():
    config['merchant_detection_method'] = merchant_detection_method_var.get()
    save_config()

## ocr region merchant?    
def update_merchant_region():
    x, y, w, h = merchant_x_var.get(), merchant_y_var.get(), merchant_width_var.get(), merchant_height_var.get()
    config['MERCHANT_OCR_TEXT_REGION'] = [x, y, w, h]
    save_config()
    display_merchant_bounding_box()

# display the merchant OCR bounding box on the screen
def display_merchant_bounding_box(scaling_factor=0.75):
    cv2.destroyAllWindows()
    region = config['MERCHANT_OCR_TEXT_REGION']
    x, y, w, h = region

    screen = np.array(pyautogui.screenshot())
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    cv2.rectangle(screen, (x, y), (x + w, y + h), (0, 0, 255), 2)

    screen_resized = cv2.resize(screen, (0, 0), fx=scaling_factor, fy=scaling_factor)
    cv2.rectangle(screen_resized, (int(x * scaling_factor), int(y * scaling_factor)), 
                  (int((x + w) * scaling_factor), int((y + h) * scaling_factor)), (0, 0, 255), 2)
    cv2.imshow('Merchant Item Name OCR Region (Scaled)', screen_resized)
    cv2.waitKey(1)

# live selection of the merchant OCR region
def live_select_merchant_region():
    screen = np.array(pyautogui.screenshot())
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

    r = cv2.selectROI("Select Region", screen, fromCenter=False, showCrosshair=True)
    x, y, w, h = r
    
    merchant_x_var.set(x)
    merchant_y_var.set(y)
    merchant_width_var.set(w)
    merchant_height_var.set(h)

    update_merchant_region()
    cv2.destroyAllWindows()

# open the Merchant OCR settings in a new window
def open_merchant_ocr_settings():
    ocr_window = tk.Toplevel(root)
    ocr_window.title("Merchant Settings")
    ocr_window.geometry("620x300")

    ttk.Label(ocr_window, text="Merchant Item Title OCR: (Live Select Region: Press C to Cancel Selection, Enter/Spacebar to choose selected region)").pack(anchor='w', pady=5)

    ocr_region_frame = ttk.Frame(ocr_window)
    ocr_region_frame.pack(anchor='w', padx=10, pady=5)

    # X and Y Coordinates with sliders
    ttk.Label(ocr_region_frame, text="X:").grid(row=1, column=0, sticky='e', padx=2)
    ttk.Scale(ocr_region_frame, from_=0, to=3000, orient='horizontal', variable=merchant_x_var).grid(row=1, column=1, columnspan=3, sticky='we', padx=2)

    ttk.Label(ocr_region_frame, text="Y:").grid(row=2, column=0, sticky='e', padx=2)
    ttk.Scale(ocr_region_frame, from_=0, to=3500, orient='horizontal', variable=merchant_y_var).grid(row=2, column=1, columnspan=3, sticky='we', padx=2)

    # Width and Height with sliders
    ttk.Label(ocr_region_frame, text="Width:").grid(row=3, column=0, sticky='e', padx=2)
    ttk.Scale(ocr_region_frame, from_=0, to=3000, orient='horizontal', variable=merchant_width_var).grid(row=3, column=1, columnspan=3, sticky='we', padx=2)

    ttk.Label(ocr_region_frame, text="Height:").grid(row=4, column=0, sticky='e', padx=2)
    ttk.Scale(ocr_region_frame, from_=0, to=3500, orient='horizontal', variable=merchant_height_var).grid(row=4, column=1, columnspan=3, sticky='we', padx=2)

    # Buttons for updating, displaying, and live selecting the region
    ttk.Button(ocr_region_frame, text="Update Region", command=update_merchant_region).grid(row=5, column=0, columnspan=2, sticky='we', pady=5)
    ttk.Button(ocr_region_frame, text="Display Bounding Box", command=display_merchant_bounding_box).grid(row=5, column=2, columnspan=2, sticky='we', pady=5)
    ttk.Button(ocr_region_frame, text="Live Select Region", command=live_select_merchant_region).grid(row=5, column=4, columnspan=2, sticky='we', pady=5)
    
    # Merchant Headshot or uhhh name method (headshot more accurate but slower, name is faster but not like headshot one so be wisely choose!)
    ttk.Label(ocr_window, text="Merchant Detection Method:").pack(anchor='w', pady=10)

    detection_method_frame = ttk.Frame(ocr_window)
    detection_method_frame.pack(anchor='w', padx=10, pady=5)

    ttk.Radiobutton(detection_method_frame, text="Name", variable=merchant_detection_method_var, value='name', command=update_merchant_detection_method).grid(row=0, column=0, sticky='w', pady=5)
    ttk.Radiobutton(detection_method_frame, text="Headshot", variable=merchant_detection_method_var, value='headshot', command=update_merchant_detection_method).grid(row=1, column=0, sticky='w', pady=5)

ttk.Button(merchant_tab, text="Open Merchant Settings", command=open_merchant_ocr_settings).pack(pady=5, padx=10)

# Merchant Auto Buy Section
merchant_auto_buy_frame = ttk.Labelframe(merchant_tab, text="Merchant Auto Buy (SEMI-WORKING, SOME ITEM WONT WORK OR FALSE PURCHASE SO BE AWARE OF THIS!)")
merchant_auto_buy_frame.pack(fill="x", padx=10, pady=5)

auto_buy_var = tk.BooleanVar(value=config.get('enable_auto_merchant', False))
auto_buy_checkbox = ttk.Checkbutton(merchant_auto_buy_frame, text="Enable Merchant Auto Buy", variable=auto_buy_var, command=save_auto_buy_setting)
auto_buy_checkbox.pack(anchor="w", padx=5, pady=2)

description_label = ttk.Label(merchant_auto_buy_frame, text="(Requires having Merchant Teleporter (costs 40 Robux) and enabling it in DolphSol Item Scheduler)")
description_label.pack(anchor="w", padx=5, pady=2)

# Mari Merchant Items Section
mari_items_frame = ttk.Labelframe(merchant_tab, text="Mari Shop Items")
mari_items_frame.pack(fill="x", padx=10, pady=5)

mari_item_options = [item['Item_To_Buy'] for item in config.get('Mari_Item_Option', [])]
mari_slot_vars = [tk.StringVar(value=config.get(f'mari_slot_{i+1}', "None")) for i in range(3)]
mari_amount_vars = [tk.IntVar(value=config.get(f'mari_amount_{i+1}', 1)) for i in range(3)]

for i in range(1, 4):
    ttk.Label(mari_items_frame, text=f"Item Slot {i}:").grid(row=i-1, column=0, sticky="w", padx=5, pady=2)
    combobox = ttk.Combobox(mari_items_frame, textvariable=mari_slot_vars[i-1], values=mari_item_options, state="readonly", width=20)
    combobox.grid(row=i-1, column=1, padx=5, pady=2)
    combobox.bind('<<ComboboxSelected>>', lambda event, i=i: update_mari_item(i, mari_slot_vars[i-1].get()))  # Pass current value of `i`
    ttk.Label(mari_items_frame, text="Amount:").grid(row=i-1, column=2, sticky="w", padx=5, pady=2)
    
    spinbox = ttk.Spinbox(mari_items_frame, from_=1, to=60, textvariable=mari_amount_vars[i-1], width=5, wrap=True)
    spinbox.grid(row=i-1, column=3, padx=5, pady=2)
    
    mari_amount_vars[i-1].trace_add('write', lambda *args, i=i: update_mari_amount(i, mari_amount_vars[i-1].get() or "1"))

# Jester Merchant Items Section
jester_items_frame = ttk.Labelframe(merchant_tab, text="Jester Shop Items (Exchange item to Dark Point will be available soon!!)")
jester_items_frame.pack(fill="x", padx=10, pady=5)

jester_item_options = [item['Item_To_Buy'] for item in config.get('Jester_Item_Option', [])]
jester_slot_vars = [tk.StringVar(value=config.get(f'jester_slot_{i+1}', "None")) for i in range(3)]
jester_amount_vars = [tk.IntVar(value=config.get(f'jester_amount_{i+1}', 1)) for i in range(3)]

for i in range(1, 4):
    ttk.Label(jester_items_frame, text=f"Item Slot {i}:").grid(row=i-1, column=0, sticky="w", padx=5, pady=2)
    combobox = ttk.Combobox(jester_items_frame, textvariable=jester_slot_vars[i-1], values=jester_item_options, state="readonly", width=20)
    combobox.grid(row=i-1, column=1, padx=5, pady=2)
    combobox.bind('<<ComboboxSelected>>', lambda event, i=i: update_jester_item(i, jester_slot_vars[i-1].get()))  # Pass current value of `i`
    ttk.Label(jester_items_frame, text="Amount:").grid(row=i-1, column=2, sticky="w", padx=5, pady=2)
    
    spinbox = ttk.Spinbox(jester_items_frame, from_=1, to=60, textvariable=jester_amount_vars[i-1], width=5, wrap=True)
    spinbox.grid(row=i-1, column=3, padx=5, pady=2)
    
    jester_amount_vars[i-1].trace_add('write', lambda *args, i=i: update_jester_amount(i, jester_amount_vars[i-1].get() or "1"))


# Bot Info Section
bot_info_frame = ttk.Labelframe(bot_tab, text="Bot Information")
bot_info_frame.pack(fill="x", padx=10, pady=5)

bot_token_var = tk.StringVar(value=os.getenv('DISCORD_BOT_TOKEN', ''))
channel_id_var = tk.StringVar(value=os.getenv('DISCORD_CHANNEL_ID', ''))
user_id_var = tk.StringVar(value=os.getenv('YOUR_DISCORD_USER_ID', ''))

ttk.Label(bot_info_frame, text="Bot Token:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
bot_token_entry = ttk.Entry(bot_info_frame, textvariable=bot_token_var, width=50)
bot_token_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(bot_info_frame, text="Channel ID:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
channel_id_entry = ttk.Entry(bot_info_frame, textvariable=channel_id_var, width=50)
channel_id_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(bot_info_frame, text="User ID:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
user_id_entry = ttk.Entry(bot_info_frame, textvariable=user_id_var, width=50)
user_id_entry.grid(row=2, column=1, padx=5, pady=5)

update_button = ttk.Button(bot_info_frame, text="Update Bot Info", command=update_bot_info)
update_button.grid(row=3, column=0, columnspan=2, pady=10)

# Bot Info Section

# Import Config Button in Settings Tab
import_config_button = ttk.Button(setting_tab, text="Import Config", command=import_config)
import_config_button.pack(pady=20, padx=10, anchor="center")


# Pack notebook (tabs) to main window
notebook.pack(expand=True, fill="both", padx=10, pady=10)

root.mainloop()

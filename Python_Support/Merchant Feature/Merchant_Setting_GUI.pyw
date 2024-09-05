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
CONFIG_FILE_PATH = BASE_DIR / 'merchant_config.json'

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


# Initialize main window
root = tk.Tk()
root.title("Python Merchant Settings (Noteab) 05/9")
root.geometry("750x380")

# Create notebook (tabs)
notebook = ttk.Notebook(root)

# NPC/Merchant Tab
merchant_tab = ttk.Frame(notebook, width=350, height=350)
notebook.add(merchant_tab, text="< Merchant/NPC Auto Buy>")

# Setting tab
setting_tab = ttk.Frame(notebook, width=350, height=350)
setting_tab.pack_propagate(False)
notebook.add(setting_tab, text="< Settings >")

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

## MERCHANT DISCORD WEBHOOK PING!
discord_userid_var = tk.StringVar(value=config.get('merchant_discord_userid', ''))
webhook_links = config.get('webhook_links', [])
mari_ping_var = tk.StringVar(value=config.get('mari_ping_userid', ''))
jester_ping_var = tk.StringVar(value=config.get('jester_ping_userid', ''))
merchant_server_link_var = tk.StringVar(value=config.get('merchant_private_server_link', ''))
merchant_ps_enabled_var = tk.BooleanVar(value=config.get('merchant_ps_link_enabled', False))

# Function to update the Discord UserID in the config
def merchant_ping_userids():
    config['mari_ping_userid'] = mari_ping_var.get()
    config['jester_ping_userid'] = jester_ping_var.get()
    save_config()

# Function to update the Private Server Link
def merchant_update_private_server_link():
    config['merchant_private_server_link'] = merchant_server_link_var.get()
    save_config()
    
def merchant_ps_link_enabled():
    config['merchant_ps_link_enabled'] = merchant_ps_enabled_var.get()
    save_config()

# Function to add a new webhook link
def add_webhook_link():
    new_link = webhook_link_var.get()
    if new_link:
        webhook_links.append(new_link)
        config['webhook_links'] = webhook_links
        save_config()
        update_webhook_listbox()

# Function to update the listbox displaying webhook links
def update_webhook_listbox():
    webhook_listbox.delete(0, tk.END)
    for link in webhook_links:
        webhook_listbox.insert(tk.END, link)

# Function to delete the selected webhook link
def delete_webhook_link():
    selected_index = webhook_listbox.curselection()
    if selected_index:
        del webhook_links[selected_index[0]]
        config['webhook_links'] = webhook_links
        save_config()
        update_webhook_listbox()

# open the Merchant OCR settings in a new window
def open_merchant_ocr_settings():
    ocr_window = tk.Toplevel(root)
    ocr_window.title("Merchant Settings")
    ocr_window.geometry("620x400")  # Fixed size window

    # Create a canvas and a scrollbar
    canvas = tk.Canvas(ocr_window)
    scrollbar = ttk.Scrollbar(ocr_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    # Configure the canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Bind mouse wheel scrolling for Windows and MacOS/Linux
    def on_mouse_wheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

    scrollable_frame.bind("<MouseWheel>", on_mouse_wheel)
    scrollable_frame.bind("<Button-4>", lambda e: on_mouse_wheel(e))
    scrollable_frame.bind("<Button-5>", lambda e: on_mouse_wheel(e))
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Merchant OCR Settings Section
    ttk.Label(scrollable_frame, text="Merchant Item Title OCR: (Live Select Region: Press C to Cancel Selection, Enter/Spacebar to choose selected region)").pack(anchor='w', pady=5)

    ocr_region_frame = ttk.Frame(scrollable_frame)
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

    # Merchant Detection Method Section
    ttk.Label(scrollable_frame, text="Merchant Detection Method:").pack(anchor='w', pady=10)

    detection_method_frame = ttk.Frame(scrollable_frame)
    detection_method_frame.pack(anchor='w', padx=10, pady=5)

    ttk.Radiobutton(detection_method_frame, text="Name", variable=merchant_detection_method_var, value='name', command=update_merchant_detection_method).grid(row=0, column=0, sticky='w', pady=5)
    ttk.Radiobutton(detection_method_frame, text="Headshot", variable=merchant_detection_method_var, value='headshot', command=update_merchant_detection_method).grid(row=1, column=0, sticky='w', pady=5)

    # Discord Webhook Management Section
    global webhook_link_var
    ttk.Label(scrollable_frame, text="Discord Webhook Management").pack(anchor='w', pady=10)
    webhook_frame = ttk.Frame(scrollable_frame)
    webhook_frame.pack(anchor='w', padx=10, pady=5)
    webhook_link_var = tk.StringVar()

    # Discord Ping User ID for Mari and Jester
    ttk.Label(scrollable_frame, text="Ping User ID if Mari found:").pack(anchor='w', pady=5)
    ttk.Entry(scrollable_frame, textvariable=mari_ping_var, width=50).pack(anchor='w', padx=10, pady=5)

    ttk.Label(scrollable_frame, text="Ping User ID if Jester found:").pack(anchor='w', pady=5)
    ttk.Entry(scrollable_frame, textvariable=jester_ping_var, width=50).pack(anchor='w', padx=10, pady=5)

    # Merchant PS link title
    ttk.Label(scrollable_frame, text="Merchant Private Server Link:").pack(anchor='w', pady=10)
    private_server_frame = ttk.Frame(scrollable_frame)
    private_server_frame.pack(anchor='w', padx=10, pady=5)

    ttk.Checkbutton(private_server_frame, text="Share Your Private Server Link If Mari/Jester Found?", variable=merchant_ps_enabled_var, command=merchant_ps_link_enabled).grid(row=0, column=0, sticky='w', pady=5)
    ttk.Entry(private_server_frame, textvariable=merchant_server_link_var, width=50).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # save userid and ps link
    ttk.Button(scrollable_frame, text="Save Ping User IDs", command=merchant_ping_userids).pack(pady=5)
    ttk.Button(scrollable_frame, text="Save Private Server Link", command=merchant_update_private_server_link).pack(pady=5)

    # webhook URL and button
    ttk.Label(webhook_frame, text="New Webhook URL:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    ttk.Entry(webhook_frame, textvariable=webhook_link_var, width=50).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(webhook_frame, text="Add Webhook", command=add_webhook_link).grid(row=0, column=2, padx=5, pady=5)

    # display existing webhooks
    global webhook_listbox
    webhook_listbox = tk.Listbox(webhook_frame, height=5, selectmode=tk.SINGLE)
    webhook_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='we')

    update_webhook_listbox()  # Populate the listbox with the current webhooks
    ttk.Button(webhook_frame, text="Delete Selected Webhook", command=delete_webhook_link).grid(row=1, column=2, padx=5, pady=5, sticky='e')

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


# Import Config Button in Settings Tab
import_config_button = ttk.Button(setting_tab, text="Import Config", command=import_config)
import_config_button.pack(pady=20, padx=10, anchor="center")

# Pack notebook (tabs) to main window
notebook.pack(expand=True, fill="both", padx=10, pady=10)

root.mainloop()

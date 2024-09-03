# Discord Import
import discord
from discord.ext import commands, tasks
from discord import app_commands

#Others Import
import os
from dotenv import load_dotenv
load_dotenv()

## Necessary Import
import autoit
import pygetwindow as gw
import time
import io
from io import BytesIO
from PIL import Image, ImageEnhance
import psutil
import win32process
import asyncio
import pytesseract
import cv2
import numpy as np
import pyautogui
import json
import re
import math
from ctypes import windll

from icecream import ic


# Load configuration json! (So cool_)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.json')
MAIN_IMAGES_PATH = os.path.join(BASE_DIR, 'images')

loop_lock = asyncio.Lock()

def load_config():
    with open(CONFIG_FILE_PATH, 'r') as f:
        config = json.load(f)
    
    default_config = {
        "merchant_detection_method": "headshot"
    }
    
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    
    save_config(config)
    return config

def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

BROWSER_EXE_NAMES = config['BROWSER_EXE_NAMES']
pytesseract.pytesseract.tesseract_cmd = config['TESSERACT_CMD']
biome_ocr_text_region = tuple(config['BIOME_OCR_TEXT_REGION'])
inventory_ocr_check_region = tuple(config['INVENTORY_OCR_CHECK_REGION'])

# Load configuration json! (So cool_)

"""
#  Save configuration usage: 
# (Step 1) config['BROWSER_EXE_NAMES'] = "chrome.exe" (define/change it after a function is executed)
# (Step 2) save_config(config) (save the changes. So your browser config is now chrome.exe)

"""

## DISCORD BOT DEFAULT SETTING ##
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
ROBLOX_WINDOW_TITLE = "Roblox"
## DISCORD BOT DEFAULT SETTING ##


## BIOME OCR ##
biomes = ["Normal", "Hell", "Starfall", "Corruption", "Glitched", "Null", "Windy", "Snowy", "Rainy"]
biome_durations = {
    "Normal": 10, 
    "Hell": 660,
    "Starfall": 600,   
    "Corruption": 660, 
    "Null": 99,
    "Glitched": 164,     
    "Windy": 120,      
    "Snowy": 120,      
    "Rainy": 120       
}


current_biome = "Normal"
biome_monitoring = False
biome_start_time = None
biome_end_time = None
is_auto_biome = config['is_auto_biome']
glitch_ping_amount = config['glitch_ping_amount']

similar_characters = {
    "1": "l",
    "n": "m",
    "m": "n",
    "t": "f",
    "f": "t",
    "s": "S",
    "S": "s",
    "w": "W",
    "W": "w"
}

def detect_glitch_biome(ocr_text):
    if not ocr_text:
        return None, None  # Return a tuple with two None values
    
    # Print the raw OCR text for reference
    #print(f"Raw OCR text: {ocr_text}")
    
    # Clean the OCR text
    cleaned_text = re.sub(r'\s', '', ocr_text)
    cleaned_text = re.sub(r'^([\[\(\{\|IJ]+)', '', cleaned_text)
    cleaned_text = re.sub(r'([\]\)\}\|IJ]+)$', '', cleaned_text)

    # Print the cleaned text
    # print(f"Cleaned OCR text: {cleaned_text}")

    # Check for glitch biome characteristics
    glitched_check = len(cleaned_text) - len(re.sub(r'\d', '', cleaned_text)) + (4 if '.' in cleaned_text else 0)

    # Determine if it's a glitched biome based on the characteristics
    if glitched_check >= 20:
        print("Detected glitched biome")
        normalized_number = re.search(r'(\d+(\.\d+)?)', cleaned_text)
        return "Glitched", normalized_number.group(1) if normalized_number else None
    
    #print("glitched fish detected. get your hp2 to catch the fish")
    return None, None


## BIOME OCR ##


## SOL'S BUTTON SCAN AND GET BUTTON POS:
game_button_positions = []

async def GameButtonScanner():
    global game_button_positions
    game_button_positions = []  # Clear the global variable

    # Load button images
    button_images = {
        "play_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\play_button.png"),
        "storage": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\storage.png"),
        "collection": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\collection.png"),
        "back_collection": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\back_collection.png"),
        "inventory": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\inventory.png"),
        "inventory_menu": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\inventory_menu_screen.png"),
        "achievement": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\achievement.png"),
        "quest": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\quest.png"),
        "setting": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\setting.png"),
        "private_server": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\PrivateServer.png"),
        "gamepass": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\gamepass.png"),
        "disconnected": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\disconnected.png"),
        "server_restart": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\server_restart.png"),
        "reconnect_skip": cv2.imread(f"{MAIN_IMAGES_PATH}\\GameButtons\\reconnect_skip.png")
    }

    screen = pyautogui.screenshot()
    screen_np = np.array(screen)
    screen_cv = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    screen_edges = cv2.Canny(screen_cv, 50, 150)

    button_count = 0
    debug_image = screen_np.copy()
    scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2] 
    
    for button_name, button_image in button_images.items():
        if button_image is None:
            continue
        
        # Convert button image to grayscale and detect edges
        button_gray = cv2.cvtColor(button_image, cv2.COLOR_BGR2GRAY)
        button_edges = cv2.Canny(button_gray, 50, 150)

        detected = False
        for scale in scale_factors:
            scaled_button_edges = cv2.resize(button_edges, (0, 0), fx=scale, fy=scale)

            if scaled_button_edges.shape[0] > screen_edges.shape[0] or scaled_button_edges.shape[1] > screen_edges.shape[1]:
                continue

            # Perform template matching on the edge-detected images
            res = cv2.matchTemplate(screen_edges, scaled_button_edges, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7
            loc = np.where(res >= threshold)

            for pt in zip(*loc[::-1]):
                if not detected:
                    button_count += 1
                    detected = True
                    center_x = pt[0] + scaled_button_edges.shape[1] // 2
                    center_y = pt[1] + scaled_button_edges.shape[0] // 2
                    game_button_positions.append((button_name, center_x, center_y))
                    cv2.rectangle(debug_image, pt, (pt[0] + scaled_button_edges.shape[1], pt[1] + scaled_button_edges.shape[0]), (0, 255, 0), 1)

            if detected:
                break

    # Optional: Save the debug image to see where buttons were detected
    # cv2.imwrite(f"{MAIN_IMAGES_PATH}/debug_game_buttons.png", debug_image)
    # ic(game_button_positions)
    
    return button_count, game_button_positions


def get_button_position(button_name):
    for name, x, y in game_button_positions:
        if name == button_name:
            return (x, y)
    return None

async def activate_roblox_window():
    try:
        all_windows = gw.getAllWindows()

        for window in all_windows:
            if "Roblox" in window.title:
                _, pid = win32process.GetWindowThreadProcessId(window._hWnd)
                process = psutil.Process(pid)
                if process.name() == "RobloxPlayerBeta.exe":
                    window.activate()
                    center_x = window.left + window.width // 2
                    center_y = window.top + window.height // 2
                    autoit.mouse_click("left", center_x, center_y)
                    return True
        return False
    except Exception as e:
        print(f"Error activating Roblox window: {e}")
        return False

def take_screenshot():
    try:
        window = gw.getWindowsWithTitle(ROBLOX_WINDOW_TITLE)[0]
        region = (window.left, window.top, window.width, window.height - 15)
        screenshot = pyautogui.screenshot(region=region)
        return screenshot
    except IndexError:
        print(f"Window with title '{ROBLOX_WINDOW_TITLE}' not found!")
        return None

def MAIN_OCR(Target_Need_To_OCR, OCR_region_type):
    try:
        if Target_Need_To_OCR == "biome":
            window = gw.getWindowsWithTitle(ROBLOX_WINDOW_TITLE)[0]
            region = (window.left + OCR_region_type[0], 
                    window.top + OCR_region_type[1], 
                    OCR_region_type[2], 
                    OCR_region_type[3])
            
            # Take a screenshot of the specified region (cheese!!)
            screenshot = pyautogui.screenshot(region=region)
            
            # Increase contrast (higher enhancer value --> higher contrast so easier to see biome font)
            image = Image.fromarray(np.array(screenshot))
            enhancer = ImageEnhance.Contrast(image)
            screenshot = enhancer.enhance(1.8)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            cv2.imwrite(f'{MAIN_IMAGES_PATH}\\biome_region.png', screenshot_cv)
            
            biome_text_result = pytesseract.image_to_string(screenshot_cv, config='--psm 7').strip()
            return biome_text_result
        
    except IndexError:
        return None
    except Exception as e:
        print(f"Error detecting biome text: {e}")
        return None

def clean_ocr_result(ocr_text):
    for biome in biomes:
        if ocr_text != None and biome.lower() in ocr_text.lower():
            return biome
    return None

def get_screen_resolution():
    user32 = windll.user32
    user32.SetProcessDPIAware()
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    return screen_width, screen_height

def convert_to_relative_coords(absolute_x, absolute_y, screen_width, screen_height, base_width=1920, base_height=1080):
    relative_x = int(absolute_x * screen_width / base_width)
    relative_y = int(absolute_y * screen_height / base_height)
    return relative_x, relative_y

async def Inventory_UseItem(item_to_use, item_quantity, item_slot, inventory_x, inventory_y, is_opened, base_width=1920, base_height=1080):
    screen_width, screen_height = get_screen_resolution()
    
    click_item_category = convert_to_relative_coords(1238, 290, screen_width, screen_height)
    search_bar_coords = convert_to_relative_coords(952, 338, screen_width, screen_height)
    quantity_coords = convert_to_relative_coords(609, 580, screen_width, screen_height)
    item_usebutton_coords = convert_to_relative_coords(716, 580, screen_width, screen_height)
    item_firstslot_coords = convert_to_relative_coords(872, 385, screen_width, screen_height)
    
    # Item slot:
    item_firstslot_coords = convert_to_relative_coords(872, 385, screen_width, screen_height) # (Use dolphSol window spy and get the client position, this is just a base xy position for 1920x1080)
    slot_offset = int(90 * screen_height / base_height) * (item_slot - 1)
    
    item_slot_coords = (
        item_firstslot_coords[0] + slot_offset,
        item_firstslot_coords[1])

    
    if is_opened == "opened":
        autoit.mouse_move(click_item_category[0], click_item_category[1], speed=5)
        autoit.mouse_click("left", click_item_category[0], click_item_category[1])
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(search_bar_coords[0], search_bar_coords[1], speed=5)
        autoit.mouse_click("left", search_bar_coords[0], search_bar_coords[1])
        await asyncio.sleep(0.5)

        autoit.send(item_to_use)
        await asyncio.sleep(0.5)
        
        autoit.mouse_move(item_slot_coords[0], item_slot_coords[1], speed=5)  #item slot click
        autoit.mouse_click("left", item_slot_coords[0], item_slot_coords[1])
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(quantity_coords[0], quantity_coords[1], speed=5)
        autoit.mouse_click("left", quantity_coords[0], quantity_coords[1])
        await asyncio.sleep(0.5)
        autoit.send(str(item_quantity))
        await asyncio.sleep(0.5)
        autoit.mouse_move(item_usebutton_coords[0], item_usebutton_coords[1], speed=5)
        autoit.mouse_click("left", item_usebutton_coords[0], item_usebutton_coords[1])
        
        await asyncio.sleep(0.5)
        
        autoit.mouse_move(quantity_coords[0], quantity_coords[1], speed=5)
        autoit.mouse_click("left", quantity_coords[0], quantity_coords[1])
        await asyncio.sleep(0.5)
        autoit.send("1")
        await asyncio.sleep(0.5)

        autoit.mouse_move(search_bar_coords[0], search_bar_coords[1], speed=5)
        autoit.mouse_click("left", search_bar_coords[0], search_bar_coords[1])
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(inventory_x, inventory_y, speed=5)
        autoit.mouse_click("left", inventory_x, inventory_y)
    
    elif is_opened == "closed":
        autoit.mouse_move(inventory_x, inventory_y, speed=10)
        autoit.mouse_click("left", inventory_x, inventory_y)
        await asyncio.sleep(0.5)
        autoit.mouse_move(click_item_category[0], click_item_category[1], speed=5)
        autoit.mouse_click("left", click_item_category[0], click_item_category[1])
        await asyncio.sleep(0.5)
        autoit.mouse_move(search_bar_coords[0], search_bar_coords[1], speed=5)
        autoit.mouse_click("left", search_bar_coords[0], search_bar_coords[1])
        autoit.send(item_to_use)
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(item_slot_coords[0], item_slot_coords[1], speed=5)  #item slot click
        autoit.mouse_click("left", item_slot_coords[0], item_slot_coords[1])
        await asyncio.sleep(0.5)


        autoit.mouse_move(quantity_coords[0], quantity_coords[1], speed=5)
        autoit.mouse_click("left", quantity_coords[0], quantity_coords[1])
        await asyncio.sleep(0.5)
        autoit.send(str(item_quantity))
        await asyncio.sleep(0.5)
        autoit.mouse_move(item_usebutton_coords[0], item_usebutton_coords[1], speed=5)
        autoit.mouse_click("left", item_usebutton_coords[0], item_usebutton_coords[1])
        
        await asyncio.sleep(0.5)
        
        autoit.mouse_move(quantity_coords[0], quantity_coords[1], speed=5)
        autoit.mouse_click("left", quantity_coords[0], quantity_coords[1])
        await asyncio.sleep(0.5)
        autoit.send("1")
        await asyncio.sleep(0.5)
        
        autoit.mouse_move(search_bar_coords[0], search_bar_coords[1], speed=5)
        autoit.mouse_click("left", search_bar_coords[0], search_bar_coords[1])
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(inventory_x, inventory_y, speed=5)
        autoit.mouse_click("left", inventory_x, inventory_y)


@bot.hybrid_command()
async def ping(ctx: commands.Context):
    await ctx.send('pong', delete_after=10)


## SYNCING COMMAND -- IMPORTANT AFTER ADDING NEW CUSTOM COMMAND, USE THIS AND REFRESH THE DISCORD IT SHOULD BE APPLIED THE EDITED CODE!
@bot.hybrid_command()
async def sync(ctx: commands.Context):
    await ctx.send(f'Syncing command from your python work... (refresh discord to apply the changes!) {ctx.author.mention}', delete_after=30)
    await bot.tree.sync()


## start command
@bot.hybrid_command()
async def start(ctx: commands.Context):
    await ctx.defer()
    await asyncio.sleep(1.4)
    
    if await activate_roblox_window():
        for _ in range(5):
            autoit.send("{f1}")
            await asyncio.sleep(0.2)
        await ctx.send("Macro started (F1 - Start button pressed)")
    else:
        await ctx.send(f"Roblox window not found! Try reconnect to the game using /reconnect?")
        
## stop command
@bot.hybrid_command()
async def stop(ctx: commands.Context):
    await ctx.defer()
    await asyncio.sleep(1.4)
    
    if await activate_roblox_window():
        for _ in range(3):
            autoit.send("{f3}")
            await asyncio.sleep(0.2)
        await ctx.send("Macro stopped (F3 - Stop button pressed)")
    else:
        await ctx.send(f"Roblox window not found! Try reconnect to the game using /reconnect? (THIS RECONNECT FEATURE STILL IN EXPERIMENTAL)")


## SCREENSHOT
@bot.hybrid_command()
async def screenshot(ctx: commands.Context):
    await ctx.defer()
    await asyncio.sleep(1.4)
    
    await activate_roblox_window()
    time.sleep(0.5)
    screenshot = take_screenshot()
    if screenshot:
        with BytesIO() as image_binary:
            screenshot.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename='epic_ss.png'), content=f"{ctx.author.mention}")
    else:
        await ctx.send("Roblox window not found!")

## REALIGN ##
@bot.hybrid_command()
async def realign(ctx: commands.Context):
    await ctx.defer()
    await asyncio.sleep(1.4)
    
    if await activate_roblox_window():
        pyautogui.hotkey('ctrl', 'f2')
        await ctx.send("Realign command executed, please wait the aligning process is finish...", delete_after=15)
    else:
        await ctx.send("Roblox window not found!")

## USE ITEM (INVENTORY) ##
item_choices = [
    app_commands.Choice(name=item['name'], value=item['value']) 
    for item in config['buff_item_choices']
]

@bot.hybrid_command()
@app_commands.describe(
    item="Choose an item to use",
    quantity="Quantity of the item to use",
    slot="Slot number where the item type is located"
)

@app_commands.choices(item=item_choices)
async def useitem(ctx: commands.Context, item: str, quantity: int = 1, slot: int = 1):
    try:
        await ctx.defer()
        await asyncio.sleep(1.4)
        
        if await activate_roblox_window():
            await GameButtonScanner()

            inventory_menu_check = get_button_position("inventory_menu")
            inventory_button = get_button_position("inventory")

            if inventory_button is None:
                await ctx.send("Error: Inventory button not found.")
                return

            autoit.send("{f2}")
            await asyncio.sleep(0.3) 

            # inventory menu title is open or closed
            is_opened = "opened" if inventory_menu_check else "closed"
            await Inventory_UseItem(item, quantity, slot, inventory_button[0], inventory_button[1], is_opened)

            await ctx.send(f"Attempted to use {item} with amount: {quantity} from slot {slot}.")
            await asyncio.sleep(0.5)
            autoit.send("{f2}")        
        else:
            await ctx.send("Roblox window not found!")

    except discord.errors.NotFound as e:
        print(f"Discord interaction expired or not found,: {e} (try again!)")
    except Exception as e:
        await ctx.send("An error occurred while processing the command.")
        print(f"Unexpected error: {e}")
        
""" RECONNECT """      
async def reconnect_function(ctx: commands.Context = None):
    if ctx:
        await ctx.defer()
        status_message = await ctx.send("Starting reconnect process...")
    else:
        status_message = None

    private_server_link_code = config.get('private_server_code', '')
    reconnect_skip = (1144, 875)

    if not private_server_link_code:
        if status_message:
            await status_message.edit(content="Private server code not found. Please make sure that you set the PS link in the Python GUI!")
        return

    launch_url = f'roblox://placeID=15532962292&linkCode={private_server_link_code}'

    # Attempt to close and reconnect the Roblox window
    if await activate_roblox_window():
        autoit.send("!{F4}")
        await asyncio.sleep(1.5)
        autoit.send("!{F4}")
        await asyncio.sleep(6)

        if status_message:
            await status_message.edit(content="Reconnecting using deep link...")
        os.system(f'start "" "{launch_url}"')

        await attempt_reconnect(status_message, reconnect_skip)
    else:
        if status_message:
            await status_message.edit(content="Roblox window not found. Attempting to reconnect...")
        await asyncio.sleep(6)

        os.system(f'start "" "{launch_url}"')

        await attempt_reconnect(status_message, reconnect_skip)


async def attempt_reconnect(status_message, reconnect_skip):
    for _ in range(45):
        if await activate_roblox_window():
            if status_message:
                await status_message.edit(content="Reconnect success. Roblox window found! Trying to press Play button...")
            if await GameButtonScanner():
                play_button = get_button_position("play_button")
                if play_button:
                    if status_message:
                        await status_message.edit(content="Play button pressed!")
                    autoit.mouse_click("left", play_button[0], play_button[1])
                    await asyncio.sleep(7.5)
                    autoit.mouse_click("left", reconnect_skip[0], reconnect_skip[1])
                    await asyncio.sleep(4)
                    autoit.mouse_wheel("down", 3)
                    await asyncio.sleep(1)
                    autoit.send("{LEFT down}")
                    await asyncio.sleep(0.5)
                    autoit.send("{LEFT up}")
                    await asyncio.sleep(0.3)
                    autoit.mouse_click_drag(967, 82, 967, 86, "right", 10)
                    await asyncio.sleep(0.8)
                    autoit.send("{f1}")
                    break
        await asyncio.sleep(1)
    else:
        if status_message:
            await status_message.edit(content="Failed to reconnect. Roblox window still not found.")

@bot.hybrid_command()
async def reconnect(ctx: commands.Context):
    await reconnect_function(ctx)
         
# Global cache for the previous button positions
previous_game_button_positions = None

@tasks.loop(seconds=25.0)
async def Disconnect_Detection_LOOP():
    enable_auto_reconnect = config['enable_reconnect']
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

    if enable_auto_reconnect:
        try:
            window = gw.getWindowsWithTitle(ROBLOX_WINDOW_TITLE)[0]
        except IndexError:
            # No Roblox window found
            await reconnect_function()
            return

        # Run the scanner and update the global cache
        button_count, game_button_positions = await GameButtonScanner()
        
        global previous_game_button_positions
        if previous_game_button_positions == game_button_positions:
            return

        # Save the current position
        previous_game_button_positions = game_button_positions

        roblox_disconnect = await asyncio.to_thread(get_button_position, "disconnected")
        server_restart = await asyncio.to_thread(get_button_position, "server_restart")

        if roblox_disconnect or server_restart:
            for _ in range(4):
                autoit.send("{f3}")
                await asyncio.sleep(0.2)

            if roblox_disconnect:
                await channel.send("Roblox disconnected popup found! Starting the reconnection soon...", delete_after=30)
            elif server_restart:
                await channel.send("Server restarting found! Starting the reconnection soon...", delete_after=30)

            await reconnect_function()
    
                
"""^^ RECONNECT ^^ """



"""BIOME OCR"""
@bot.hybrid_command()
async def biome(ctx: commands.Context):
    await ctx.defer()
    if await activate_roblox_window():
        time.sleep(0.3)
        biome_text = MAIN_OCR("biome", biome_ocr_text_region)
        cleaned_biome_text = clean_ocr_result(biome_text)
        
        
        if cleaned_biome_text:
            await asyncio.sleep(0.4)
            await ctx.send(f"Current Biome: {cleaned_biome_text}")
            await ctx.send(file=discord.File(f'{MAIN_IMAGES_PATH}\\biome_region.png'))
        else:
            await asyncio.sleep(0.4)
            await ctx.send("Biome text cannot be recognized because the game environment might be covering the biome font. Possible biome:")
            await ctx.send(file=discord.File(f'{MAIN_IMAGES_PATH}\\biome_region.png'))
            

        
"""AUTO BIOME OCR"""           
@bot.hybrid_command()
async def auto_biome(ctx: commands.Context, enable_auto_biome: bool):
    global biome_monitoring, biome_start_time, biome_end_time
    await ctx.defer()
    if await activate_roblox_window() and enable_auto_biome:
        biome_monitoring = True
        biome_start_time = time.time() 
        await ctx.send(f"Activated Auto Biome {ctx.author.mention}", delete_after=30)
    elif await activate_roblox_window() and not enable_auto_biome:
        biome_monitoring = False
        biome_start_time = None
        biome_end_time = None
        await ctx.send(f"Deactivated Auto Biome {ctx.author.mention}", delete_after=30)
    
    ## CONFIG UPDATE ##   
    config['is_auto_biome'] = enable_auto_biome
    save_config(config)


@tasks.loop(seconds=2.0)
async def AUTO_BIOME_SEARCH_LOOP():
    global current_biome, biome_monitoring, biome_start_time, biome_end_time
    if biome_monitoring:
        channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
        biome_text = MAIN_OCR("biome", biome_ocr_text_region)
        cleaned_biome_text = clean_ocr_result(biome_text)
        glitch_biome_detected, normalized_glitch_number = detect_glitch_biome(biome_text)  # Now expecting two values
        if glitch_biome_detected:
            await activate_roblox_window()
            cleaned_biome_text = glitch_biome_detected
            # ic(f"Glitched Biome Detected During Wait: {biome_text}")
            
            if channel:
                DISCORD_user_id = os.getenv('YOUR_DISCORD_USER_ID')
                if DISCORD_user_id:
                    for _ in range(glitch_ping_amount):
                        await channel.send(f"<@{DISCORD_user_id}> **!! Glitch Biome Detected (BE CAUTION) !!**\n"
                                           f"OCR Biome Text: {biome_text}\n"
                                           f"Normalized Number: {normalized_glitch_number}\n")
                        await asyncio.sleep(1)
                    await channel.send(file=discord.File(f'{MAIN_IMAGES_PATH}\\biome_region.png'))

        if biome_text and cleaned_biome_text and cleaned_biome_text != current_biome and cleaned_biome_text != "Normal":
            current_biome = cleaned_biome_text
            biome_start_time = time.time()  # Reset start time for the new biome
            duration = biome_durations.get(cleaned_biome_text, 0)

            # Calculate the adjusted remaining duration if started late
            if biome_end_time:
                elapsed_time = time.time() - biome_start_time
                remaining_time = max(duration - elapsed_time, 0)
            else:
                remaining_time = duration

            biome_end_time = time.time() + remaining_time

            if channel:
                await channel.send(f"Rare Biome Found: {cleaned_biome_text}")
                await channel.send(file=discord.File(f'{MAIN_IMAGES_PATH}\\biome_region.png'))
                biome_monitoring = False
                bot.loop.create_task(wait_for_biome_duration(remaining_time))

async def wait_for_biome_duration(duration):
    global current_biome, biome_monitoring, biome_start_time, biome_end_time
    check_interval = 1  # Interval to re-check the biome during its duration
    elapsed_time = 0

    while elapsed_time < duration:
        await asyncio.sleep(check_interval)
        elapsed_time += check_interval
        
        biome_text = MAIN_OCR("biome", biome_ocr_text_region)
        cleaned_biome_text = clean_ocr_result(biome_text)
        channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

        
        glitch_biome_detected, normalized_glitch_number = detect_glitch_biome(biome_text)  # Now expecting two values
        if glitch_biome_detected:
            await activate_roblox_window()
            current_biome = glitch_biome_detected
            #ic(f"Glitched Biome Detected During Wait: {biome_text}")

            if channel:
                DISCORD_user_id = os.getenv('YOUR_DISCORD_USER_ID')
                if DISCORD_user_id:
                    for _ in range(glitch_ping_amount):
                        await channel.send(f"<@{DISCORD_user_id}> **!! Glitch Biome Detected (BE CAUTION) !!**\n"
                                           f"OCR Biome Text: {biome_text}\n"
                                           f"Normalized Number: {normalized_glitch_number}\n")
                        await asyncio.sleep(1)
                    await channel.send(file=discord.File(f'{MAIN_IMAGES_PATH}\\biome_region.png'))
                biome_monitoring = True  # Reset monitoring after glitch biome detection and notification
                return

        if biome_text and cleaned_biome_text and cleaned_biome_text != current_biome and cleaned_biome_text != "Normal":
            current_biome = cleaned_biome_text
            biome_start_time = time.time()
            new_duration = biome_durations.get(cleaned_biome_text, 0)
            elapsed_time = 0  # Reset the timer for the new biome
            duration = new_duration
            biome_end_time = time.time() + duration
            
            if channel:
                await channel.send(f"Rare Biome Found: {cleaned_biome_text}")
                await channel.send(file=discord.File(f'{MAIN_IMAGES_PATH}\\biome_region.png'))

    biome_monitoring = True

"""AUTO BIOME OCR""" 
        

## AUTO ITEM CRAFTING MECHANIC ##
item_crafting_positions = []

def get_item_crafting_position(button_name):
    for name, x, y in item_crafting_positions:
        if name == button_name:
            return (x, y)
    return None

async def item_crafting_image_process():
    global item_crafting_positions
    
    main_item_craft_images = {
        "open_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\jake_open_button.png"),
        "close_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\close_button.png"),
        "auto_add_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\auto_add_button.png"),
        "craft_item_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\craft_item_button.png"),
        
        "Gear Basing": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\gear_basing.png"),
        "Luck Glove": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\luck_glove.png"),
        "Lunar Device": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\lunar_device.png"),
        "Solar Device": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\solar_device.png"),
        "Subzero Device": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\subzero_device.png"),
        "Eclipse": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\eclipse.png"),
        "Eclipse Device": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\eclipse_device.png"),
        "Exo Gauntlet": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\exo_gauntlet.png"),
        "Jackpot Gauntlet": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\jackpot_gauntlet.png"),
        "Gravitational Device": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\gravitational_device.png"),
        "Windstorm Device": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\windstorm_device.png"),
        "Volcanic Device": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\volcanic_device.png"),
        "Biome Randomizer": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\biome_randomizer.png"),
        "Strange Controller": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\strange_controller.png"),
        "Flesh Device": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\flesh_device.png")
        
    }

    screen = pyautogui.screenshot()
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    item_crafting_positions = []
    for button_name, button_image in main_item_craft_images.items():
        if button_image is None:
            continue
        res = cv2.matchTemplate(screen_cv, button_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        
        detected = False
        for pt in zip(*loc[::-1]):
            if not detected:
                detected = True
                center_x = pt[0] + button_image.shape[1] // 2
                center_y = pt[1] + button_image.shape[0] // 2
                item_crafting_positions.append((button_name, center_x, center_y))
    
    return item_crafting_positions


async def AUTO_ITEM_CRAFTING_PATH_AND_CRAFT_LOGIC(item_to_craft):
    pyautogui.press("f2")
    await asyncio.sleep(1)
    await activate_roblox_window()
    autoit.send("{ESC}")
    await asyncio.sleep(0.3)
    autoit.send("r")
    await asyncio.sleep(0.3)
    autoit.send("{ENTER}")
    await asyncio.sleep(1.3)
    autoit.send("{w down}")
    await asyncio.sleep(1.7)
    autoit.send("{a down}")
    autoit.send("{w up}")
    await asyncio.sleep(3.2)
    autoit.send("{a up}")
    await asyncio.sleep(0.5)
    autoit.send("f")
    
    # Wait for a moment and then process item crafting buttons
    for _ in range(20):
        if await item_crafting_image_process():
            open_button_pos = get_item_crafting_position("open_button")
            
            if open_button_pos:
                autoit.mouse_click("left", open_button_pos[0], open_button_pos[1])
                break
            else:
                print("Open Button not found. Crafting process cannot continue.")
        
        await asyncio.sleep(1)
    
    # After open, wait it to do image search and click the target item
    found = False
    for _ in range(70):
        for _ in range(4):  # Try to find the item up to 4 times
            if await item_crafting_image_process():
                target_item_pos = get_item_crafting_position(item_to_craft)
                auto_add_button = get_item_crafting_position("auto_add_button")
                craft_item_button = get_item_crafting_position("craft_item_button")
                close_button = get_item_crafting_position("close_button")

                if target_item_pos:
                    found = True
                    autoit.mouse_move(target_item_pos[0], target_item_pos[1])
                    await asyncio.sleep(0.5)
                    autoit.mouse_click("left", target_item_pos[0], target_item_pos[1])
                    await asyncio.sleep(0.7)
                    autoit.mouse_move(target_item_pos[0] + 500, target_item_pos[1])
                    await asyncio.sleep(0.7)

                    if craft_item_button:
                        autoit.mouse_click("left", craft_item_button[0], craft_item_button[1])
                        await asyncio.sleep(0.3)

                    if auto_add_button:
                        autoit.mouse_click("left", auto_add_button[0], auto_add_button[1])
                        await asyncio.sleep(0.3)
                        autoit.mouse_move(321, 478) # move to item list
                        await asyncio.sleep(0.5)
                        autoit.mouse_wheel("up", 10) # Scroll up to above to default item slot

                    if close_button:
                        autoit.mouse_click("left", close_button[0], close_button[1])
                        await asyncio.sleep(1)
                        autoit.send("{esc}")
                        await asyncio.sleep(0.3)
                        autoit.send("r")
                        autoit.send("{enter}")
                        await asyncio.sleep(1.3)
                        pyautogui.press("f2")
                    break
                else:
                    """Target item not found. Scrolling to find item"""
                    
                    autoit.mouse_move(321, 478) # move to item list
                    await asyncio.sleep(0.5)
                    autoit.mouse_wheel("down", 4) # Scroll down to search for the item
                    await asyncio.sleep(0.6)
                    
                    # Reprocess image search after scrolling
                    await item_crafting_image_process()
        
            if found:
                break
        
        if found:
            break
        else:
            autoit.mouse_wheel("up", 12)  # Reset scroll
            await asyncio.sleep(1)
            break


@tasks.loop(minutes=int(config['crafting_interval']))
async def AUTO_ITEM_CRAFTING_LOOP():
    auto_item_crafting = config['enable_auto_item_crafting']

    if auto_item_crafting:
        async with loop_lock:
            if await activate_roblox_window():
                slot_items = [
                    config.get("slot_1"),
                    config.get("slot_2"),
                    config.get("slot_3")
                ]

                if not hasattr(AUTO_ITEM_CRAFTING_LOOP, 'current_slot'):
                    AUTO_ITEM_CRAFTING_LOOP.current_slot = 0

                item_to_craft = slot_items[AUTO_ITEM_CRAFTING_LOOP.current_slot]

                if item_to_craft and item_to_craft.strip().lower() != "none":
                    print(f"Preparing to craft item in Slot {AUTO_ITEM_CRAFTING_LOOP.current_slot + 1}: {item_to_craft}")
                    try:
                        await AUTO_ITEM_CRAFTING_PATH_AND_CRAFT_LOGIC(item_to_craft) 
                        print(f"Crafted item in Slot {AUTO_ITEM_CRAFTING_LOOP.current_slot + 1}: {item_to_craft}")
                    except Exception as e:
                        print(f"Error while crafting item in Slot {AUTO_ITEM_CRAFTING_LOOP.current_slot + 1}: {e}")
                else:
                    print(f"No valid item assigned to Slot {AUTO_ITEM_CRAFTING_LOOP.current_slot + 1}. Skipping...")

                AUTO_ITEM_CRAFTING_LOOP.current_slot = (AUTO_ITEM_CRAFTING_LOOP.current_slot + 1) % len(slot_items)

    await asyncio.sleep(0.1)

""" MERCHANT FEATURE """
Merchant_ON_PROCESS_LOOP = False
detected_positions = set()
MERCHANT_Item_Position = []
MERCHANT_SHOP_BUTTON_Position = []


def get_merchant_buttons_position(button_name):
    for name, x, y in MERCHANT_SHOP_BUTTON_Position:
        if name == button_name:
            return (x, y)
    return None

def is_Merchant_ITEM_nearby(position1, position2, threshold=7):
    """Check if two positions are within a certain threshold distance."""
    distance = math.sqrt((position1[0] - position2[0]) ** 2 + (position1[1] - position2[1]) ** 2)
    return distance <= threshold

def feature_based_matching(screen_cv, template, ratio_threshold=0.60):
    screen_gray = cv2.cvtColor(screen_cv, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Create SIFT detector
    sift = cv2.SIFT_create()

    # Find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(screen_gray, None)
    kp2, des2 = sift.detectAndCompute(template_gray, None)

    if des1 is None or des2 is None:
        return None, screen_cv

    # find matches
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des2, des1, k=2)

    # Apply ratio test to get good matches
    good_matches = []
    for m, n in matches:
        if m.distance < ratio_threshold * n.distance:
            good_matches.append(m)

    # Use homography to filter the matches further
    if len(good_matches) > 8:  # Minimum number of points required for homography
        src_pts = np.float32([kp2[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp1[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if M is not None:
            matchesMask = mask.ravel().tolist()

            # Draw bounding box
            h, w = template.shape[:2]
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)

            # detected bounding box is fully within the screen bounds
            screen_h, screen_w = screen_cv.shape[:2]
            if (dst[:, 0, 0].min() >= 0 and dst[:, 0, 1].min() >= 0 and 
                dst[:, 0, 0].max() <= screen_w and dst[:, 0, 1].max() <= screen_h):
                
                # check to sure the bounding box size is correct
                detected_width = dst[:, 0, 0].max() - dst[:, 0, 0].min()
                detected_height = dst[:, 0, 1].max() - dst[:, 0, 1].min()
                
                #ic(f"detected_width: {detected_width}", f"withd: {w}")
                #ic(f"detected_height: {detected_height}", f"withd: {h}")
                
                if detected_width >= w * 0.85 and detected_height >= h * 0.85:
                    screen_cv = cv2.polylines(screen_cv, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)
                    return (int(dst[0][0][0]), int(dst[0][0][1])), screen_cv
                
            else:
                return None, screen_cv
            
    return None, screen_cv

async def Merchant_Specific_Item_SCANNING_Process(merchant_type, item_name, threshold=0.75, ratio_threshold=0.75):
    """Scan for a specific item in the merchant's inventory and return the position if found."""
    
    Merchant_Items_Image = {
        "mari": {
            "Mixed Potion": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Mixed_Pot.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Mixed_Pot_Green.png")
            ],
            
            "Mixed Potion Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Mixed Potion_Shop_Item_Name.png")
            ],
            
            "Fortune Spoid 1": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_1.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_1_Blue.png")
            ],
            
            "Fortune Spoid 1 Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Fortune Spoid 1_Shop_Item_Name.png")
            ],
            
            "Fortune Spoid 2 ": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_2.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_2_Blue.png")
            ],
            
            "Fortune Spoid 2 Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Fortune Spoid 2_Shop_Item_Name.png")
            ],
            
            "Fortune Spoid 3": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_3.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Fortune Spoid 3_Shop_Item_Name.png")
            ],
            
            "Fortune Spoid 3 Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Fortune Spoid 3_Shop_Item_Name.png")
            ],
            
            "Lucky Potion": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Lucky_Pot.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Lucky_Pot_Green.png")
            ],
            
            "Lucky Potion Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Lucky Potion_Shop_Item_Name.png")
            ],
            
            "Lucky Potion XL": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Lucky_PotXL.png")
            ],
            
            "Lucky Potion XL Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Lucky Potion XL_Shop_Item_Name.png")
            ],
            
            "Speed Potion": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Speed_Pot.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Speed_Pot_Green.png")
            ],
            
            "Speed Potion Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Speed Potion_Shop_Item_Name.png")
            ],
             
            "Speed Potion L": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Speed_PotL.png")
            ],
            
            "Speed Potion L Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Speed Potion L_Shop_Item_Name.png")
            ],
            
            "Speed Potion XL": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Speed_PotXL.png")
            ],
            
            "Speed Potion XL Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Speed Potion XL_Shop_Item_Name.png")
            ],
            
            "Gear A": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\GearA.png")
            ],
            
            "Gear A Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Gear A_Shop_Item_Name.png")
            ],
            
            "Gear B": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\GearB.png")   
            ],
            
            "Gear B Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Gear B_Shop_Item_Name.png")       
            ],
            
            "Lucky Penny": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Lucky_Penny.png")     
            ],
            
            "Lucky Penny Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Lucky Penny_Shop_Item_Name.png")               
            ],
            
            "Void Coin": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Void_Coin.png"),
            ],
            
            "Void Coin Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Item_Shop_Name\\Void Coin_Shop_Item_Name.png")  
            ] 
        },
        "jester": {
            "Oblivion Potion": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester's\\Oblivion_Pot.png"),
            ],
            
            "Oblivion Potion Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester's\\Item_Shop_Name\\Oblivion Potion_Shop_Item_Name.png")  
            ],
                
            "Heavenly Potion 2": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester's\\Heavenly_Pot2.png")
            ],
            
            "Heavenly Potion 2 Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester's\\Item_Shop_Name\\Heavenly Potion 2_Shop_Item_Name.png")
            ],
            
            "Merchant Tracker": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester's\\Tracker.png")
            ],
            
            "Merchant Tracker Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester's\\Item_Shop_Name\\Merchant Tracker_Shop_Item_Name.png")
            ],
            
            "Rune Of Everything": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester's\\Rune_Everything.png")
            ],
            
            "Rune Of Everything Item Name": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester's\\Item_Shop_Name\\Rune Of Everything_Shop_Item_Name.png")
            ]
        }
    }


    if merchant_type not in Merchant_Items_Image or item_name not in Merchant_Items_Image[merchant_type]:
        return None

    # Capture the current screen
    screen_resolution = get_screen_resolution()
    base_resolution = screen_resolution
    
    screen = pyautogui.screenshot()
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    screen_resolution = screen_cv.shape[1], screen_cv.shape[0]

    all_matches = []

    # Get the list of images associated with the item
    item_images = Merchant_Items_Image[merchant_type][item_name]

    for item_image in item_images:
        if item_image is None:
            continue

        # Scale the template image based on the user's screen resolution
        scaling_factor = (screen_resolution[0] / base_resolution[0], screen_resolution[1] / base_resolution[1])
        scaled_item_image = cv2.resize(item_image, (0, 0), fx=scaling_factor[0], fy=scaling_factor[1])

        if "_Item Name" in item_name:
            screen_gray = cv2.cvtColor(screen_cv, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(scaled_item_image, cv2.COLOR_BGR2GRAY)

            # Apply Canny edge detection
            screen_can = cv2.Canny(screen_gray, 50, 150)
            template_edges = cv2.Canny(template_gray, 50, 150)
            
            res = cv2.matchTemplate(screen_can, template_edges, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)

            detected = False
            for pt in zip(*loc[::-1]):
                if not detected:
                    detected = True
                    center_x = pt[0] + template_edges.shape[1] // 2
                    center_y = pt[1] + template_edges.shape[0] // 2

                    # Region for feature matching
                    x, y = pt[0], pt[1]
                    roi = screen_cv[y:y + template_gray.shape[0], x:x + template_gray.shape[1]]

                    # feature-based matching
                    best_match, roi_with_match = feature_based_matching(roi, scaled_item_image, ratio_threshold=ratio_threshold)

                    if best_match:
                        cv2.circle(screen_cv, (center_x, center_y), 10, (0, 255, 0), 3)
                        cv2.imwrite(f"{MAIN_IMAGES_PATH}/{item_name}_debug.png", screen_cv)
                        all_matches.append((item_name, center_x, center_y, threshold))
                    break
        else:
            best_match, screen_with_match = feature_based_matching(screen_cv, scaled_item_image, ratio_threshold=ratio_threshold)

            if best_match:
                x, y = best_match
                detected_width, detected_height = scaled_item_image.shape[1], scaled_item_image.shape[0]
                
                center_x = x + detected_width // 2
                center_y = y + detected_height // 2
                
                # Debug
                cv2.circle(screen_with_match, (center_x, center_y), 10, (0, 255, 0), 3)
                cv2.imwrite(f"{MAIN_IMAGES_PATH}/{item_name}_detected_debug.png", screen_with_match)

                all_matches.append((item_name, center_x, center_y, ratio_threshold))
                break

    if all_matches:
        best_match = all_matches[0]
        return best_match[:3]
    else:
        print(f"No match found for {item_name}.")
        return None

    if all_matches:
        best_match = all_matches[0]
        return best_match[:3]
    else:
        print(f"No match found for {item_name}.")
        return None
    

async def Merchant_Button_SCANNING_Process(debug=False):
    global MERCHANT_SHOP_BUTTON_Position

    Merchant_Buttons_Image = {
        "open_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\jake_open_button.png"),
        "jester_open_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester_Open_Button.png"),
        "Exchange_Button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Exchange.png")
        # "Purchase_Amount": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Purchase_Amount.png"),
        # "Purchase_Button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Purchase_Button.png")
    }

    # Get screen resolution
    screen_resolution = get_screen_resolution()
    base_resolution = (1920, 1080)

    # Capture current screen
    screen = pyautogui.screenshot()
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    screen_gray = cv2.cvtColor(screen_cv, cv2.COLOR_BGR2GRAY)

    # Scaling factor based on the current screen resolution compared to the base resolution
    scaling_factor = (screen_resolution[0] / base_resolution[0], screen_resolution[1] / base_resolution[1])

    MERCHANT_SHOP_BUTTON_Position = []

    for button_name, button_image in Merchant_Buttons_Image.items():
        if button_image is None:
            continue

        # Resize the template based on the user's screen resolution
        button_image_gray = cv2.cvtColor(button_image, cv2.COLOR_BGR2GRAY)
        scaled_button_image = cv2.resize(button_image_gray, (0, 0), fx=scaling_factor[0], fy=scaling_factor[1])

        res = cv2.matchTemplate(screen_gray, scaled_button_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.75
        loc = np.where(res >= threshold)

        detected = False
        for pt in zip(*loc[::-1]):
            if not detected:
                detected = True
                center_x = pt[0] + scaled_button_image.shape[1] // 2
                center_y = pt[1] + scaled_button_image.shape[0] // 2
                MERCHANT_SHOP_BUTTON_Position.append((button_name, center_x, center_y))

                if debug:
                    print(f"Debug: {button_name.capitalize()} detected at position: ({center_x}, {center_y})")
                break

        # Edge detection fallback if nothing was detected
        if not detected:
            edges_button_image = cv2.Canny(scaled_button_image, 50, 150)
            edges_screen = cv2.Canny(screen_gray, 50, 150)

            res = cv2.matchTemplate(edges_screen, edges_button_image, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)

            for pt in zip(*loc[::-1]):
                center_x = pt[0] + edges_button_image.shape[1] // 2
                center_y = pt[1] + edges_button_image.shape[0] // 2
                MERCHANT_SHOP_BUTTON_Position.append((button_name, center_x, center_y))

                if debug:
                    print(f"Debug: {button_name.capitalize()} detected using edge detection at position: ({center_x}, {center_y})")
                break

    return MERCHANT_SHOP_BUTTON_Position


async def Merchant_Headshot_Process(merchant_type, debug=False):
    """Process to detect the merchant by NPC name and return their name position, with resolution scaling support."""

    merchant_images = {
        "mari": {
            "headshot": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari_Headshot.png"),
            "name": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari_Name.png")
        },
        "jester": {
            "headshot": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester_Headshot.png"),
            "name": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester_Name.png")
        }
    }

    if merchant_type not in merchant_images:
        print(f"Invalid merchant type specified: {merchant_type}")
        return None

    # Get the detection method and current screen resolution
    scan_method = config.get('merchant_detection_method', 'headshot').lower()
    screen_width, screen_height = get_screen_resolution()
    
    if scan_method not in merchant_images[merchant_type]:
        print(f"Invalid scan method '{scan_method}' for merchant type '{merchant_type}'")
        return None

    merchant_image = merchant_images[merchant_type][scan_method]

    if merchant_image is None:
        print(f"Error: {scan_method.capitalize()} image for {merchant_type} is not loaded properly.")
        return None

    # Use current screen resolution as the base for scaling
    scaling_factor_x = screen_width / 1920
    scaling_factor_y = screen_height / 1080 
    resized_merchant_image = cv2.resize(merchant_image, (0, 0), fx=scaling_factor_x, fy=scaling_factor_y)
    
    # Capture the current screen
    screen = pyautogui.screenshot()
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    # Perform template matching
    res = cv2.matchTemplate(screen_cv, resized_merchant_image, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    detected_positions = []

    # Check if any positions were detected
    if len(loc[0]) > 0:
        detected_positions = [
            (pt[0] + resized_merchant_image.shape[1] // 2, pt[1] + resized_merchant_image.shape[0] // 2)
            for pt in zip(*loc[::-1])
        ]
        if debug:
            print(f"Debug: {merchant_type.capitalize()} detected using {scan_method} at positions: {detected_positions}")
        return detected_positions
    else:
        if debug:
            print(f"Debug: No {merchant_type.capitalize()} detected using {scan_method} on screen.")
        return None
    
async def Merchant_Shop_Title_Process(merchant_type, debug=False):
    """Process to detect the merchant's shop title and return the position if found."""
    
    merchant_shop_title_images = {
        "mari": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari_Shop.png"),
        "jester": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester_Shop.png")
    }
    
    if merchant_type not in merchant_shop_title_images:
        return None

    shop_title_image = merchant_shop_title_images[merchant_type]

    if shop_title_image is None:
        print(f"Error: Shop title image for {merchant_type} is not loaded properly.")
        return None


    shop_title_image_gray = cv2.cvtColor(shop_title_image, cv2.COLOR_BGR2GRAY)
    screen = pyautogui.screenshot()
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    # Convert screen to grayscale
    screen_gray = cv2.cvtColor(screen_cv, cv2.COLOR_BGR2GRAY)
    scales = [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]  

    for scale in scales:
        resized_shop_title = cv2.resize(shop_title_image_gray, (0, 0), fx=scale, fy=scale)
        
        res = cv2.matchTemplate(screen_gray, resized_shop_title, cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        loc = np.where(res >= threshold)
        
        detected_positions = []

        if len(loc[0]) > 0:
            detected_positions = [(pt[0] + resized_shop_title.shape[1] // 2, pt[1] + resized_shop_title.shape[0] // 2) for pt in zip(*loc[::-1])]
            if debug:
                print(f"Debug: {merchant_type.capitalize()} shop title detected at scale {scale} at positions: {detected_positions}")
            return detected_positions

    edges_shop_title = cv2.Canny(shop_title_image_gray, 50, 150)
    edges_screen = cv2.Canny(screen_gray, 50, 150)

    res = cv2.matchTemplate(edges_screen, edges_shop_title, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) > 0:
        detected_positions = [(pt[0] + edges_shop_title.shape[1] // 2, pt[1] + edges_shop_title.shape[0] // 2) for pt in zip(*loc[::-1])]
        if debug:
            print(f"Debug: {merchant_type.capitalize()} shop title detected using edge detection at positions: {detected_positions}")
        return detected_positions

    if debug:
        print(f"Debug: No {merchant_type.capitalize()} shop title detected on screen.")
    
    return None

def get_merchant_item_config_slots(config):
    merchant_item_slots = {
        "mari": {
            "mari_slot_1": (config.get("mari_slot_1", "None"), config.get("mari_amount_1", 1)),
            "mari_slot_2": (config.get("mari_slot_2", "None"), config.get("mari_amount_2", 1)),
            "mari_slot_3": (config.get("mari_slot_3", "None"), config.get("mari_amount_3", 1))
        },
        "jester": {
            "jester_slot_1": (config.get("jester_slot_1", "None"), config.get("jester_amount_1", 1)),
            "jester_slot_2": (config.get("jester_slot_2", "None"), config.get("jester_amount_2", 1)),
            "jester_slot_3": (config.get("jester_slot_3", "None"), config.get("jester_amount_3", 1))
        }
    }
    return merchant_item_slots

async def MERCHANT_scroll_and_rescan(merchant_type, item_name):
    """Handles scrolling and rescanning for items."""
    Merchant_screen_width, Merchant_screen_height = get_screen_resolution()
    item_scroll_pos = convert_to_relative_coords(926, 707, Merchant_screen_width, Merchant_screen_height)
    
    autoit.mouse_move(item_scroll_pos[0], item_scroll_pos[1])
    autoit.mouse_wheel("down", 4)
    await asyncio.sleep(1.5)

    item_positions = await Merchant_Specific_Item_SCANNING_Process(merchant_type, item_name, threshold=0.75, ratio_threshold=0.5)
    return item_positions


async def purchase_items(merchant_type, item_slots, bought_items, side, screen_width, screen_height, max_retries=6):
    """Helper function to handle item purchases with retry mechanism and dynamic ratio threshold."""
    
    for slot_name, (item_name, amount) in item_slots.items():
        if item_name == "None" or item_name in bought_items:
            continue

        print(f"Attempting to purchase item {item_name} from the {side} side with amount {amount}.")

        item_positions = None
        for attempt in range(max_retries):
            item_positions = await Merchant_Specific_Item_SCANNING_Process(
                merchant_type, item_name, threshold=0.75, ratio_threshold=0.78
            )
            if item_positions: 
                break
            else: 
                await asyncio.sleep(0.25)

        if not item_positions:
            print(f"Failed to detect item {item_name} after {max_retries} attempts. Skipping item.")
            continue

        detected_item_name, center_x, center_y = item_positions
        print(f"Detected {detected_item_name} at ({center_x}, {center_y}).")

        await asyncio.sleep(0.2)
        autoit.mouse_click("left", center_x, center_y)
        await asyncio.sleep(0.5)

        # Retry loop for double-checking with the item shop name with decreasing ratio threshold
        item_shop_name_positions = None
        initial_ratio_threshold = 0.8
        
        for attempt in range(max_retries):
            current_ratio_threshold = initial_ratio_threshold - (0.05 * attempt)
            item_shop_name_positions = await Merchant_Specific_Item_SCANNING_Process(
                merchant_type, f"{item_name} Item Name", threshold=0.75, ratio_threshold=current_ratio_threshold
            )
            if item_shop_name_positions:
                print(f"Double-check successful for {item_name} on attempt {attempt + 1} with ratio threshold {current_ratio_threshold:.2f}.")
                break
            else:
                print(f"Double-check failed for {item_name} on attempt {attempt + 1} with ratio threshold {current_ratio_threshold:.2f}. Retrying...")
                await asyncio.sleep(0.12)

        if not item_shop_name_positions:
            print(f"Failed to double-check item {item_name} after {max_retries} attempts. Skipping purchase.")
            continue

        # Perform button scanning to find purchase-related buttons
        purchase_amount_pos = convert_to_relative_coords(659, 596, screen_width, screen_height)
        purchase_button_pos = convert_to_relative_coords(702, 648, screen_width, screen_height)

        if purchase_amount_pos:
            autoit.mouse_click("left", purchase_amount_pos[0], purchase_amount_pos[1])
            autoit.send(str(amount))
            await asyncio.sleep(0.25)

        if purchase_button_pos:
            autoit.mouse_click("left", purchase_button_pos[0], purchase_button_pos[1])
            await asyncio.sleep(4)

        # Log the item as bought
        bought_items.add(item_name)
            
async def Merchant_Item_Buy_Process(merchant_type):
    """Process to purchase items from the merchant, while checking if the merchant is still present."""
    
    Merchant_screen_width, Merchant_screen_height = get_screen_resolution()
    config = load_config()
    merchant_item_slots = get_merchant_item_config_slots(config)

    max_attempts = 10
    attempts = 0
    button_positions = None
    bought_items = set()

    #  # Retry loop for Merchant_Button_SCANNING_Process
    # while attempts < 5:
    #     button_positions = await Merchant_Button_SCANNING_Process()
    #     if button_positions:
    #         print(f"Detected general buttons for {merchant_type}.")
    #         break
    #     else:
    #         attempts += 1
    #         await asyncio.sleep(0.25)

    # if not button_positions:
    #     print(f"Failed to detect general buttons for {merchant_type} after {max_attempts} attempts. Using pixel coord method..")
    
    await asyncio.sleep(5.6)
    autoit.send("{F2}")
    await asyncio.sleep(0.5)
    await activate_roblox_window()
    await asyncio.sleep(0.4)
    
    # Get button positions (fallback to manual pixel coordinates if detection fails)
    # jester_open_button_pos = get_merchant_buttons_position("jester_open_button")
    # open_button_pos = get_merchant_buttons_position("open_button")
    
    open_button_pos = convert_to_relative_coords(609, 875, Merchant_screen_width, Merchant_screen_height)
    autoit.mouse_click("left", open_button_pos[0], open_button_pos[1])

    # Step 1: Scroll down to the right side (where rare items should be here i think)
    await asyncio.sleep(0.5)
    item_scroll_pos = convert_to_relative_coords(926, 720, Merchant_screen_width, Merchant_screen_height)
    autoit.mouse_move(item_scroll_pos[0], item_scroll_pos[1])
    autoit.mouse_wheel("up", 8)
    await asyncio.sleep(0.5)
    autoit.mouse_wheel("down", 3)
    await asyncio.sleep(0.4)

    # Send Merchant's Item Screenshot
    await Merchant_Items_Webhook_Sender(merchant_type, "")
    await purchase_items(merchant_type, merchant_item_slots[merchant_type], bought_items, "right", Merchant_screen_width, Merchant_screen_height)
    
    # Step 2: Scroll back up to the left side (common items)
    autoit.mouse_move(item_scroll_pos[0], item_scroll_pos[1])
    autoit.mouse_wheel("up", 8)
    await asyncio.sleep(0.4)

    # Send Merchant's Item Screenshot
    await purchase_items(merchant_type, merchant_item_slots[merchant_type], bought_items, "left", Merchant_screen_width, Merchant_screen_height)

    await merchant_reset_macro_phase()

async def merchant_reset_macro_phase():
    autoit.send("{ESC}")
    autoit.send("r")
    await asyncio.sleep(0.4)
    autoit.send("{ENTER}")
    await asyncio.sleep(1.3)
    autoit.mouse_wheel("up", 15)
    await asyncio.sleep(1.2)
    autoit.mouse_wheel("down", 10)
    await asyncio.sleep(1.2)
    autoit.send("{F2}")
    

async def Merchant_Webhook_Sender(Merchant_Name):
    """Sends a webhook message with a screenshot if a merchant is detected."""
    screenshot = take_screenshot()
    DISCORD_user_id = os.getenv('YOUR_DISCORD_USER_ID')
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
    
    if screenshot:
        with BytesIO() as image_binary:
            screenshot.save(image_binary, 'PNG')
            image_binary.seek(0)

            # Prepare the embed with the screenshot
            embed = discord.Embed(
                title=f"{Merchant_Name.capitalize()} Detected!",
                description=f"{Merchant_Name.capitalize()} has been detected on your screen.",
                color=discord.Color.blue() if Merchant_Name == "mari" else discord.Color.purple()
            )
            
            thumbnail_url = (
                "https://static.wikia.nocookie.net/sol-rng/images/3/37/MARI_HIGH_QUALITYY.png/revision/latest?cb=20240704045119"
                if Merchant_Name == "mari" else
                "https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest?cb=20240630142936"
            )
            
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_image(url="attachment://epic_ss.png")
            embed.add_field(name="Merchant Face Screenshot", value="", inline=False)
            embed.set_footer(text="Auto Merchant Detection")

            if channel:
                await channel.send(
                    f"<@{DISCORD_user_id}>", 
                    embed=embed, 
                    file=discord.File(fp=image_binary, filename='epic_ss.png')
                )
            else:
                print("Channel not found or invalid channel ID.")
    else:
        print("Roblox window not found!")

async def Merchant_Items_Webhook_Sender(Merchant_Name, extra_info):
    """Sends a webhook message with a screenshot of the merchant's items."""
    screenshot = take_screenshot()
    DISCORD_user_id = os.getenv('YOUR_DISCORD_USER_ID')
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
    
    if screenshot:
        with BytesIO() as inventory_binary:
            screenshot.save(inventory_binary, 'PNG')
            inventory_binary.seek(0)
            
            # Create the embed for inventory
            inventory_embed = discord.Embed(
                title=f"{Merchant_Name.capitalize()}'s Shop Items",
                color=discord.Color.blue() if Merchant_Name == "mari" else discord.Color.purple()
            )
            inventory_embed.add_field(name=f"Item Screenshot {extra_info}", value="", inline=False)
            inventory_embed.set_image(url="attachment://inventory_ss.png")
            inventory_embed.set_footer(text="Auto Merchant Detection")
            
            if channel:
                await channel.send(
                    embed=inventory_embed, 
                    file=discord.File(fp=inventory_binary, filename='inventory_ss.png')
                )
            else:
                print("Channel not found or invalid channel ID.")

@tasks.loop(seconds=4)
async def AUTO_MERCHANT_DETECTION_LOOP():
    """Automatically detect merchants and handle item buying process."""
    global Merchant_ON_PROCESS_LOOP

    if Merchant_ON_PROCESS_LOOP: return

    auto_merchant_detection = config.get('enable_auto_merchant', False)

    if not auto_merchant_detection: return

    async with loop_lock:  # Lock this loop to prevent interfering actions from auto craft loop or other loops
        merchants = {
            'mari': False,
            'jester': False
        }

        tasks = []

        for merchant in merchants:
            positions = await Merchant_Headshot_Process(merchant)
            if positions:
                print(f"{merchant.capitalize()} detected!")
                merchants[merchant] = True
                Merchant_ON_PROCESS_LOOP = True

                # Create the tasks for webhook notification and item buying process
                webhook_task = asyncio.create_task(Merchant_Webhook_Sender(merchant))
                buy_process_task = asyncio.create_task(Merchant_Item_Buy_Process(merchant))

                tasks.append(webhook_task)
                tasks.append(buy_process_task)

        # Wait for all tasks to complete
        if tasks:
            try: await asyncio.gather(*tasks)
            except Exception as e: print(f"An error occurred during merchant processing: {e}")
            finally: Merchant_ON_PROCESS_LOOP = False

        if not any(merchants.values()):
            await asyncio.sleep(2)
            
""" MERCHANT FEATURE """


## AUTO ITEM CRAFTING MECHANIC ##
@bot.event
async def on_ready():
    print(f'{bot.user} has joined your playground!')
    global biome_monitoring
    biome_monitoring = is_auto_biome ## set biome_monitoring from loaded config
    AUTO_BIOME_SEARCH_LOOP.start()
    AUTO_ITEM_CRAFTING_LOOP.start()
    Disconnect_Detection_LOOP.start()
    AUTO_MERCHANT_DETECTION_LOOP.start()
    #await bot.tree.sync() # Uncomment it when you sync the bot for the first time like the tutorial video, after synced successfully, you can comment it or delete it to prevent bot ratelimit
bot.run(os.getenv('DISCORD_BOT_TOKEN')) 



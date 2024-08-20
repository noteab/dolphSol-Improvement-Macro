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
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import psutil
import win32process
import asyncio
import pytesseract
import cv2
import numpy as np
import pyautogui
import json
import re
from ctypes import windll
from icecream import ic

# Load configuration json! (So cool_)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.json')
MAIN_IMAGES_PATH = os.path.join(BASE_DIR, 'images')

def load_config():
    with open(CONFIG_FILE_PATH, 'r') as f:
        config = json.load(f)
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
biomes = ["Normal", "Hell", "Starfall", "Corruption", "Null", "Windy", "Snowy", "Rainy"]
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


def detect_glitch_biome(ocr_text):
    """ HOW IT WORK:
    Detects a glitched biome in the given OCR text.

    Parameters:
    - ocr_text (str): The OCR text to analyze.

    Returns:
    - str: "Glitched" if a glitched biome is detected, else None.
    """
    # Regex pattern to match potential glitched biome numbers with flexible brackets and misread characters
    glitch_biome_pattern = re.compile(
        r'[\[\{\(\|]?\s*[0O@©]\s*[\.,]\s*\d*[\da-zA-Z]*\s*[\]\}\)\|]?'
    )

    # Search for all potential matches in the OCR text
    matches = ''
    
    if ocr_text != None: matches = glitch_biome_pattern.findall(ocr_text)
       
   
    if matches:
        for match in matches:
            potential_number = match.strip()

            # Debugging Output
            #ic(f"Potential Match Found: {match}")

            normalized_number = potential_number.replace('@', '0').replace('©', '0').replace('O', '0')
            normalized_number = normalized_number.replace(',', '.')
            normalized_number = re.sub(r'[^\d.]', '', normalized_number)  # Remove all non-digit and non-period characters


            # Validate if the normalized string is a valid decimal number
            try:
                float_value = float(normalized_number)
                # Glitched biome numbers are between 0 and 1:
                if 0.0 < float_value < 1.0:
                    return "Glitched", normalized_number
            except ValueError:
                continue  # If conversion fails, proceed to check the next match one i guess?

    return None

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

    window = gw.getWindowsWithTitle(ROBLOX_WINDOW_TITLE)[0]

    region = (window.left, window.top, window.width, window.height - 10)

    screen = pyautogui.screenshot(region=region)
    screen_np = np.array(screen)
    screen_cv = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

    button_count = 0
    debug_image = screen_np.copy()
    

    for button_name, button_image in button_images.items():
        # Ensure the image was loaded successfully
        if button_image is None:
            print(f"Error: Failed to load image for '{button_name}'")
            continue
        
        button_cv = cv2.cvtColor(button_image, cv2.COLOR_RGB2BGR)

        # Check if the template (button_cv) is larger than the screenshot region (screen_cv)
        if button_cv.shape[0] > screen_cv.shape[0] or button_cv.shape[1] > screen_cv.shape[1]:
            print(f"Error: Button image '{button_name}' is larger than the your screen region. Skipping to prevent further error...")
            print(f"Button size: {button_cv.shape}, Screen size: {screen_cv.shape}")
            continue

        res = cv2.matchTemplate(screen_cv, button_cv, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)

        detected = False
        for pt in zip(*loc[::-1]):
            if not detected:
                button_count += 1
                detected = True
                center_x = pt[0] + button_image.shape[1] // 2
                center_y = pt[1] + button_image.shape[0] // 2
                game_button_positions.append((button_name, center_x, center_y))
            cv2.rectangle(debug_image, pt, (pt[0] + button_image.shape[1], pt[1] + button_image.shape[0]), (0, 255, 0), 1)

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
    
    
    click_item_category = (1238, 290) # higher y -> the mouse will go down (Use dolphSol window spy and get the client position, this is just a base xy position for 1920x1080)
    search_bar_coords = (952, 338) # higher y -> the mouse will go down (Use dolphSol window spy and get the client position, this is just a base xy position for 1920x1080)
    quantity_coords = (609, 580) # higher y -> the mouse will go down (Use dolphSol window spy and get the client position, this is just a base xy position for 1920x1080)
    
    item_usebutton_coords = (716, 580) # higher y -> the mouse will go down (Use dolphSol window spy and get the client position, this is just a base xy position for 1920x1080)
    
    # Item slot:
    item_firstslot_coords = (872, 385) # (Use dolphSol window spy and get the client position, this is just a base xy position for 1920x1080)
    slot_offset = int(90 * screen_height / base_height) * (item_slot - 1)
    
    item_slot_coords = (
        item_firstslot_coords[0] + slot_offset,
        item_firstslot_coords[1])

    
    if is_opened == "opened":
        autoit.mouse_move(click_item_category[0], click_item_category[1], speed=10)
        autoit.mouse_click("left", click_item_category[0], click_item_category[1])
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(search_bar_coords[0], search_bar_coords[1], speed=10)
        autoit.mouse_click("left", search_bar_coords[0], search_bar_coords[1])
        await asyncio.sleep(0.5)

        autoit.send(item_to_use)
        await asyncio.sleep(0.5)
        
        autoit.mouse_move(item_slot_coords[0], item_slot_coords[1], speed=10)  #item slot click
        autoit.mouse_click("left", item_slot_coords[0], item_slot_coords[1])
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(quantity_coords[0], quantity_coords[1], speed=10)
        autoit.mouse_click("left", quantity_coords[0], quantity_coords[1])
        await asyncio.sleep(0.5)
        autoit.send(str(item_quantity))
        await asyncio.sleep(0.5)
        autoit.mouse_move(item_usebutton_coords[0], item_usebutton_coords[1], speed=10)
        autoit.mouse_click("left", item_usebutton_coords[0], item_usebutton_coords[1])
        
        await asyncio.sleep(0.5)
        
        autoit.mouse_move(quantity_coords[0], quantity_coords[1], speed=10)
        autoit.mouse_click("left", quantity_coords[0], quantity_coords[1])
        await asyncio.sleep(0.5)
        autoit.send("1")
        await asyncio.sleep(0.5)

        autoit.mouse_move(search_bar_coords[0], search_bar_coords[1], speed=10)
        autoit.mouse_click("left", search_bar_coords[0], search_bar_coords[1])
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(inventory_x, inventory_y, speed=10)
        autoit.mouse_click("left", inventory_x, inventory_y)
    
    elif is_opened == "closed":
        autoit.mouse_move(inventory_x, inventory_y, speed=10)
        autoit.mouse_click("left", inventory_x, inventory_y)
        await asyncio.sleep(0.5)
        autoit.mouse_move(click_item_category[0], click_item_category[1], speed=10)
        autoit.mouse_click("left", click_item_category[0], click_item_category[1])
        await asyncio.sleep(0.5)
        autoit.mouse_move(search_bar_coords[0], search_bar_coords[1], speed=10)
        autoit.mouse_click("left", search_bar_coords[0], search_bar_coords[1])
        autoit.send(item_to_use)
        
        await asyncio.sleep(0.5)
        autoit.mouse_move(item_slot_coords[0], item_slot_coords[1], speed=10)  #item slot click
        autoit.mouse_click("left", item_slot_coords[0], item_slot_coords[1])
        await asyncio.sleep(0.5)


        autoit.mouse_move(quantity_coords[0], quantity_coords[1], speed=10)
        autoit.mouse_click("left", quantity_coords[0], quantity_coords[1])
        await asyncio.sleep(0.5)
        autoit.send(str(item_quantity))
        await asyncio.sleep(0.5)
        autoit.mouse_move(item_usebutton_coords[0], item_usebutton_coords[1], speed=10)
        autoit.mouse_click("left", item_usebutton_coords[0], item_usebutton_coords[1])
        
        await asyncio.sleep(0.5)
        
        autoit.mouse_move(quantity_coords[0], quantity_coords[1], speed=10)
        autoit.mouse_click("left", quantity_coords[0], quantity_coords[1])
        await asyncio.sleep(0.5)
        autoit.send("1")
        await asyncio.sleep(0.5)
        
        autoit.mouse_move(search_bar_coords[0], search_bar_coords[1], speed=10)
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
    if await activate_roblox_window():
        for _ in range(5):
            autoit.send("{f1}")
            await asyncio.sleep(0.2)
        await ctx.send("Macro stopped (F1 - Start button pressed)")
    else:
        await ctx.send(f"Roblox window not found! Try reconnect to the game using /reconnect?")
        
## stop command
@bot.hybrid_command()
async def stop(ctx: commands.Context):
    await ctx.defer()
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
    await ctx.defer()

    if await activate_roblox_window():
        await GameButtonScanner()

        # Get positions of inventory buttons
        inventory_menu_check = get_button_position("inventory_menu")
        inventory_button = get_button_position("inventory")

        # Check if positions were found
        if inventory_button is None:
            await ctx.send("Error: Inventory button not found.")
            return
        
        autoit.send("{f2}")
        await asyncio.sleep(0.3) 

        # Determine whether the inventory menu title is open or closed
        is_opened = "opened" if inventory_menu_check else "closed"
        await Inventory_UseItem(item, quantity, slot, inventory_button[0], inventory_button[1], is_opened)

        await ctx.send(f"Attempted to use {item} with amount: {quantity} from slot {slot}.")
        await asyncio.sleep(0.5)
        autoit.send("{f2}")        
    else:
        await ctx.send("Roblox window not found!")
        
""" RECONNECT """      
async def reconnect_function(ctx: commands.Context = None):
    if ctx:
        await ctx.defer()
        status_message = await ctx.send("Starting reconnect process...")
    else:
        status_message = None

    private_server_link_code = config.get('private_server_code', '')
    reconnect_skip = (1144, 875)  # Replace with the correct coordinates for your resolution

    if not private_server_link_code:
        if status_message:
            await status_message.edit(content="Private server code not found. Please make sure that you set the PS link in the Python GUI!")
        return

    launch_url = f'roblox://placeID=15532962292&linkCode={private_server_link_code}'

    # Attempt to close and reconnect the Roblox window
    if await activate_roblox_window():
        autoit.send("!{F4}")  # Close the active Roblox window
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

        # Compare with previous result (if any) to avoid repeated actions
        global previous_game_button_positions
        if previous_game_button_positions == game_button_positions:
            return

        # Save the current positions for future comparison
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
    
        
        result = detect_glitch_biome(biome_text)
        if result:
            await activate_roblox_window()
            glitch_biome_detected, normalized_glitch_number = result
            cleaned_biome_text = glitch_biome_detected
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

        if cleaned_biome_text and cleaned_biome_text != current_biome and cleaned_biome_text != "Normal":
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
                await channel.send(f"Biome Found: {cleaned_biome_text}")
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

        
        result = detect_glitch_biome(biome_text)
        if result:
            await activate_roblox_window()
            glitch_biome_detected, normalized_glitch_number = result
            cleaned_biome_text = glitch_biome_detected
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

        if cleaned_biome_text and cleaned_biome_text != current_biome and cleaned_biome_text != "Normal":
            current_biome = cleaned_biome_text
            biome_start_time = time.time()
            new_duration = biome_durations.get(cleaned_biome_text, 0)
            elapsed_time = 0  # Reset the timer for the new biome
            duration = new_duration
            biome_end_time = time.time() + duration
            
            if channel:
                await channel.send(f"Latest biome found: {cleaned_biome_text}")
                await channel.send(file=discord.File(f'{MAIN_IMAGES_PATH}\\biome_region.png'))

    biome_monitoring = True  # Reset monitoring after biome duration ends

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
    
    window = gw.getWindowsWithTitle(ROBLOX_WINDOW_TITLE)[0]
    region = (window.left, window.top, window.width, window.height - 10)
    screen = pyautogui.screenshot(region=region)
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    item_crafting_positions = []
    for button_name, button_image in main_item_craft_images.items():
        if button_image is None:
            continue
        res = cv2.matchTemplate(screen_cv, button_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8  # Adjust threshold as needed
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
            # If not found after trying both scroll directions, reset and break the loop
            autoit.mouse_wheel("up", 12)  # Reset scroll
            await asyncio.sleep(1)
            break


    
# @bot.hybrid_command()
# async def item_craft_test(ctx: commands.Context, item_craft_test: str):
#     await ctx.defer()
#     if await activate_roblox_window():
#         await AUTO_ITEM_CRAFTING_PATH_AND_CRAFT_LOGIC(item_craft_test)
#         await ctx.send("Done item crafting test", delete_after=10)

@tasks.loop(minutes=int(config['crafting_interval']))
async def AUTO_ITEM_CRAFTING_LOOP():
    auto_item_crafting = config['enable_auto_item_crafting']
    
    if auto_item_crafting:
        if await activate_roblox_window():
            slot_items = [
                config.get("slot_1"),
                config.get("slot_2"),
                config.get("slot_3")
            ]

            if not hasattr(AUTO_ITEM_CRAFTING_LOOP, 'current_slot'):
                AUTO_ITEM_CRAFTING_LOOP.current_slot = 0

            # Get the item to craft for the current slot
            item_to_craft = slot_items[AUTO_ITEM_CRAFTING_LOOP.current_slot]

            # Check if the item is valid
            if item_to_craft and item_to_craft.strip().lower() != "none":
                print(f"Preparing to craft item in Slot {AUTO_ITEM_CRAFTING_LOOP.current_slot + 1}: {item_to_craft}")
                await AUTO_ITEM_CRAFTING_PATH_AND_CRAFT_LOGIC(item_to_craft) 
                print(f"Crafted item in Slot {AUTO_ITEM_CRAFTING_LOOP.current_slot + 1}: {item_to_craft}")
            else:
                print(f"No valid item assigned to Slot {AUTO_ITEM_CRAFTING_LOOP.current_slot + 1}. Skipping...")

            # Move to the next slot for the next loop iteration
            AUTO_ITEM_CRAFTING_LOOP.current_slot = (AUTO_ITEM_CRAFTING_LOOP.current_slot + 1) % len(slot_items)
            

""" MERCHANT FEATURE """
MERCHANT_Button_Position = []

async def send_merchant_embed(merchant_name, screenshot):
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
    embed = discord.Embed(
        title="Merchant Detected!",
        description=f"{merchant_name} has been found.",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://example.com/merchant_thumbnail.png")  # Optional: Add a thumbnail for the embed
    
    # Convert screenshot to a file-like object
    image_bytes = io.BytesIO()
    screenshot.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    file = discord.File(fp=image_bytes, filename="merchant_screenshot.png")
    
    embed.set_image(url="attachment://merchant_screenshot.png")
    
    await channel.send(embed=embed, file=file)
    
def get_merchant_buttons_position(button_name):
    for name, x, y in MERCHANT_Button_Position:
        if name == button_name:
            return (x, y)
    return None

async def Merchant_Button_Process(merchant_type):
    global MERCHANT_Button_Position
    
    merchant_check_assets = {
        "merchant_open": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jake_Shop\\jake_open_button.png"),
        "merchant_exchange": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Exchange.png"),
        "merchant_purchase_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Purchase_Button.png"),
        "merchant_purchase_amount": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Purchase_Amount.png"),
        "Mari_Name": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari_Name.png"),
        "Jester_Name": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Jester_Name.png"),
    }
    
    mari_assets = {
        "Void Coin": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Void_Coin.png"),
        "Lucky Penny": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Lucky_Penny.png"),
        "Lucky Potion XL": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Lucky_PotXL.png"),
        "Mixed Potion": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Mixed_Pot.png"),
        "Fortune Spoid 3": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_3.png"),
        "Fortune Spoid 1": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_1.png"),
    }
    
    jester_assets = {
        "Void Coin": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Void_Coin.png"),
        "Lucky Penny": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Lucky_Penny.png"),
        "Lucky Potion XL": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Lucky_PotXL.png"),
        "Mixed Potion": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Mixed_Pot.png"),
        "Fortune Spoid 3": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_3.png"),
        "Fortune Spoid 1": cv2.imread(f"{MAIN_IMAGES_PATH}\\Merchants\\Mari's\\Fortune_Spoid_1.png"),
    }
    
    window = gw.getWindowsWithTitle(ROBLOX_WINDOW_TITLE)[0]
    region = (window.left, window.top, window.width, window.height - 10)
    screen = pyautogui.screenshot(region=region)
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    MERCHANT_Button_Position = []
    
    for button_name, button_image in merchant_check_assets.items():
        if button_image is None:
            continue
        
        if button_image.shape[0] > screen_cv.shape[0] or button_image.shape[1] > screen_cv.shape[1]:
            print(f"Error: Button image '{button_name}' is larger than your screen region. Skipping to prevent further error...")
            continue
        
        res = cv2.matchTemplate(screen_cv, button_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.75
        loc = np.where(res >= threshold)
        
        detected = False
        for pt in zip(*loc[::-1]):
            if not detected:
                detected = True
                center_x = pt[0] + button_image.shape[1] // 2
                center_y = pt[1] + button_image.shape[0] // 2
                MERCHANT_Button_Position.append((button_name, center_x, center_y))
    
    return MERCHANT_Button_Position

async def Merchant_Item_Process(merchant_type):
    slot_names = [f"{merchant_type}_slot_1", f"{merchant_type}_slot_2", f"{merchant_type}_slot_3"]
    
    for slot in slot_names:
        item_name = config[slot]
        if item_name == "None":
            continue
        
        item_found = False
        
        for _ in range(3):  # Try scrolling up to 3 times to find the item
            await Merchant_Button_Process()
            item_position = get_merchant_buttons_position(item_name)
            
            if item_position:
                item_found = True
                print(f"Item {item_name} found at position {item_position}.")
                autoit.mouse_click("left", item_position[0], item_position[1])
                
                purchase_amount_pos = get_merchant_buttons_position("merchant_purchase_amount")
                if purchase_amount_pos:
                    autoit.mouse_click("left", purchase_amount_pos[0], purchase_amount_pos[1])
                    await asyncio.sleep(0.4)
                    autoit.send("1")  # Default amount is 1
                    purchase_button_pos = get_merchant_buttons_position("merchant_purchase_button")
                    await asyncio.sleep(0.4)
                    if purchase_button_pos:
                        autoit.mouse_click("left", purchase_button_pos[0], purchase_button_pos[1])
                        print(f"Purchased {item_name}.")
                break
            else:
                autoit.mouse_wheel("down", 4)
                await asyncio.sleep(1)
        
        if not item_found:
            print(f"Item {item_name} not found after scrolling. Skipping to next item.")

@tasks.loop(seconds=5)
async def AUTO_MERCHANT_DETECTION_LOOP():
    auto_merchant_detection = config['enable_auto_merchant_detection']
    
    if auto_merchant_detection:
        print("Checking for merchants in the background...")
        
        merchant_name_found = False
        merchant_interacted = False
        
        for _ in range(70):
            await Merchant_Button_Process()
            
            for merchant_name in ["Mari_Name", "Jester_Name"]:
                merchant_position = get_merchant_buttons_position(merchant_name)
                
                if merchant_position:
                    merchant_name_found = True
                    merchant_type = "mari" if merchant_name == "Mari_Name" else "jester"
                    print(f"Merchant {merchant_type} found at position {merchant_position}.")
                    
                    autoit.mouse_click("left", merchant_position[0], merchant_position[1])
                    await asyncio.sleep(2.3)
                    
                    open_button_pos = get_merchant_buttons_position("merchant_open")
                    
                    if open_button_pos:
                        autoit.mouse_click("left", open_button_pos[0], open_button_pos[1])
                        print("Merchant shop opened.")
                        merchant_interacted = True
                        await Merchant_Item_Process(merchant_type)
                        break
                    # else:
                    #     print("Open Button not found. Retrying...")
            
            if merchant_interacted:
                break
            else:
                await asyncio.sleep(1)
        
        if not merchant_name_found:
            print("No merchant detected in the area. Rechecking in the next loop...")
    
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
    
    #await bot.tree.sync() # Uncomment it when you sync the bot for the first time like the tutorial video, after synced successfully, you can comment it or delete it to prevent bot ratelimit
  
  

bot.run(os.getenv('DISCORD_BOT_TOKEN'))

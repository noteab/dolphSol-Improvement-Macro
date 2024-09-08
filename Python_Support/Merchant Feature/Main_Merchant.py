# Discord Import
import discord
from discord.ext import commands, tasks
from discord import app_commands

#Others Import
import os

## Necessary Import
import pydirectinput
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
from fuzzywuzzy import fuzz
from ctypes import windll
import aiohttp
import subprocess
from icecream import ic

ROBLOX_WINDOW_TITLE = "Roblox"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'merchant_config.json')
MAIN_IMAGES_PATH = os.path.join(BASE_DIR, 'Merchants_Image')
loop_lock = asyncio.Lock()

def load_config():
    with open(CONFIG_FILE_PATH, 'r') as f:
        config = json.load(f)
    
    return config

def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()
pytesseract.pytesseract.tesseract_cmd = config['TESSERACT_CMD']

## Coordinate ##
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

## Active roblox window ##
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

## Active roblox window ##
        
## Screenshot ##
def take_screenshot():
    try:
        window = gw.getWindowsWithTitle(ROBLOX_WINDOW_TITLE)[0]
        region = (window.left, window.top, window.width, window.height - 15)
        screenshot = pyautogui.screenshot(region=region)
        return screenshot
    except IndexError:
        print(f"Window with title '{ROBLOX_WINDOW_TITLE}' not found!")
        return None
## Screenshot ##   
    
""" MERCHANT FEATURE """
Merchant_ON_PROCESS_LOOP = False
detected_positions = set()
MERCHANT_Item_Position = []
MERCHANT_SHOP_BUTTON_Position = []
merchant_cooldown_end_time = 0

def get_merchant_buttons_position(button_name):
    for name, x, y in MERCHANT_SHOP_BUTTON_Position:
        if name == button_name:
            return (x, y)
    return None

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

def compare_histograms(img1, img2):
    """Compare the color histograms of two images and return True if they are look similar"""
    
    hist_img1 = cv2.calcHist([img1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist_img2 = cv2.calcHist([img2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    hist_img1 = cv2.normalize(hist_img1, hist_img1)
    hist_img2 = cv2.normalize(hist_img2, hist_img2)

    similarity = cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_CORREL)
    return similarity > 0.85

async def Merchant_Specific_Item_SCANNING_Process(merchant_type, item_name, threshold=0.75, ratio_threshold=0.75, ocr_double_check=False):
    
    Merchant_Items_Image = {
        "mari": {
            "Mixed Potion": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Mixed_Pot.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Mixed_Pot_Green.png")
            ],
            
            
            "Fortune Spoid 1": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Fortune_Spoid_1.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Fortune_Spoid_1_Blue.png")
            ],
            
            
            "Fortune Spoid 2 ": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Fortune_Spoid_2.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Fortune_Spoid_2_Blue.png")
            ],
            
            
            "Fortune Spoid 3": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Fortune_Spoid_3.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Item_Shop_Name\\Fortune Spoid 3_Shop_Item_Name.png")
            ],
            
            
            "Lucky Potion": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Lucky_Pot.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Lucky_Pot_Green.png")
            ],
        
            
            "Lucky Potion XL": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Lucky_PotXL.png")
            ],
            
            
            "Speed Potion": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Speed_Pot.png"),
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Speed_Pot_Green.png")
            ],
            
             
            "Speed Potion L": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Speed_PotL.png")
            ],
            
            
            "Speed Potion XL": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Speed_PotXL.png")
            ],
            
            
            "Gear A": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\GearA.png")
            ],
            
            
            "Gear B": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\GearB.png")   
            ],
        
            
            "Lucky Penny": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Lucky_Penny.png")     
            ],
            
            
            "Void Coin": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari's\\Void_Coin.png"),
            ],
            
        },
        "jester": {
            "Oblivion Potion": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Oblivion_Pot.png"),
            ],
            
            "Heavenly Potion 1": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Heavenly_Pot1.png")
            ],
            
            "Heavenly Potion 2": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Heavenly_Pot2.png")
            ],
                       
            "Merchant Tracker": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Tracker.png")
            ],
            
            "Stella Candle": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Stella_Candle.png")
            ],
            
            "Strange Potion 1": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Strange_Pot1.png")
            ],
            
            "Strange Potion 2": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Strange_Pot2.png")
            ],
            
            "Random Potion Sack": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Random_Sack.png")
            ],
            
            "Rune Of Everything": [
                cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester's\\Rune_Everything.png")
            ],
            
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
    
    item_images = Merchant_Items_Image[merchant_type][item_name]

    for item_image in item_images:
        if item_image is None:
            continue
        
        scaling_factor = (screen_resolution[0] / base_resolution[0], screen_resolution[1] / base_resolution[1])
        scaled_item_image = cv2.resize(item_image, (0, 0), fx=scaling_factor[0], fy=scaling_factor[1])

        # OCR double check
        if ocr_double_check:
            MERCHANT_OCR_TEXT_REGION = config.get("MERCHANT_OCR_TEXT_REGION", [759, 386, 323, 29])
            x, y, w, h = MERCHANT_OCR_TEXT_REGION
            cropped_region = screen_cv[y:y+h, x:x+w]

            # Perform OCR on the cropped region
            extracted_text = pytesseract.image_to_string(cropped_region, config='--psm 7').strip()
            
            #ic(f"Extracted OCR Text: {extracted_text}")
            
            match_score = fuzz.ratio(extracted_text.lower(), item_name.lower())

            if match_score > 80:
                print(f"OCR Match: '{extracted_text}' (score: {match_score}) matches expected '{item_name}'")
                center_x, center_y = x + w // 2, y + h // 2
                all_matches.append((item_name, center_x, center_y, ratio_threshold))
            else:
                print(f"OCR Mismatch: Expected '{item_name}', but got '{extracted_text}' with match score {match_score}")
                
        else:
            best_match, screen_with_match = feature_based_matching(screen_cv, scaled_item_image, ratio_threshold=ratio_threshold)
            if best_match:
                x, y = best_match
                detected_width, detected_height = scaled_item_image.shape[1], scaled_item_image.shape[0]
                center_x = x + detected_width // 2
                center_y = y + detected_height // 2

                # debug
                cv2.circle(screen_with_match, (center_x, center_y), 10, (0, 255, 0), 3)
                cv2.imwrite(f"{MAIN_IMAGES_PATH}/{item_name}_detected_debug.png", screen_with_match)
                
                return (item_name, center_x, center_y, ratio_threshold)
                
    if not all_matches:
        print(f"No match found for {item_name} using feature base, switching to historic")
        for item_image in item_images:
            if item_image is None:
                continue
             
        scales = [1.0, 0.9, 0.8, 0.7, 1.1]
        for scale in scales:
            scaled_item_image = cv2.resize(item_image, (0, 0), fx=scale, fy=scale)
            res = cv2.matchTemplate(screen_cv, scaled_item_image, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)

            for pt in zip(*loc[::-1]):
                center_x = pt[0] + scaled_item_image.shape[1] // 2
                center_y = pt[1] + scaled_item_image.shape[0] // 2
                all_matches.append((item_name, center_x, center_y))

        # Histogram compare for false detection check
        for match in all_matches:
            x, y = match[1], match[2]
            detected_region = screen_cv[y:y + scaled_item_image.shape[0], x:x + scaled_item_image.shape[1]]
            if compare_histograms(item_image, detected_region):
                return match[:3] # :3

    if all_matches:
        best_match = all_matches[0]
        return best_match[:3]
    else:
        print(f"No match found for {item_name}.")
        return None
    

async def Merchant_Button_SCANNING_Process(debug=False):
    global MERCHANT_SHOP_BUTTON_Position

    Merchant_Buttons_Image = {
        "open_button": cv2.imread(f"{MAIN_IMAGES_PATH}\\jake_open_button.png"),
        "Exchange_Button": cv2.imread(f"{MAIN_IMAGES_PATH}\\Exchange.png")
    }

    # Get screen resolution
    screen_resolution = get_screen_resolution()
    base_resolution = (1920, 1080)

    # Capture current screen and convert to grayscale
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

        # Perform template matching
        res = cv2.matchTemplate(screen_gray, scaled_button_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        loc = np.where(res >= threshold)

        if len(loc[0]) > 0:  # Button found, exit early
            for pt in zip(*loc[::-1]):
                center_x = pt[0] + scaled_button_image.shape[1] // 2
                center_y = pt[1] + scaled_button_image.shape[0] // 2
                MERCHANT_SHOP_BUTTON_Position.append((button_name, center_x, center_y))

                if debug:
                    print(f"Debug: {button_name.capitalize()} detected at position: ({center_x}, {center_y})")
                break 

        # Fallback to edge detection if nothing was detected
        if len(loc[0]) == 0:
            edges_button_image = cv2.Canny(scaled_button_image, 50, 150)
            edges_screen = cv2.Canny(screen_gray, 50, 150)

            res = cv2.matchTemplate(edges_screen, edges_button_image, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)

            if len(loc[0]) > 0:
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
            "headshot": cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari_Headshot.png"),
            "name": cv2.imread(f"{MAIN_IMAGES_PATH}\\Mari_Name.png")
        },
        "jester": {
            "headshot": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester_Headshot.png"),
            "name": cv2.imread(f"{MAIN_IMAGES_PATH}\\Jester_Name.png")
        }
    }

    if merchant_type not in merchant_images:
        print(f"Invalid merchant type specified: {merchant_type}")
        return None

    # Get the detection method and current screen resolution
    scan_method = config.get('merchant_detection_method', 'headshot').lower()
    
    if scan_method not in merchant_images[merchant_type]:
        print(f"Invalid scan method '{scan_method}' for merchant type '{merchant_type}'")
        return None

    merchant_image = merchant_images[merchant_type][scan_method]

    if merchant_image is None:
        print(f"Error: {scan_method.capitalize()} image for {merchant_type} is not loaded properly.")
        return None

    # Define a threshold for template matching
    threshold = 0.75

    # Capture the current screen
    start_time = time.time()
    screen = pyautogui.screenshot()
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    # scales for faster detection
    detected_positions = None
    scales = [1.2, 1.1, 1.0, 0.9, 0.8] 

    for scale in scales:
        resized_merchant_image = cv2.resize(merchant_image, (0, 0), fx=scale, fy=scale)
        res = cv2.matchTemplate(screen_cv, resized_merchant_image, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        if len(loc[0]) > 0:
            detected_positions = [
                (pt[0] + resized_merchant_image.shape[1] // 2, pt[1] + resized_merchant_image.shape[0] // 2)
                for pt in zip(*loc[::-1])
            ]
            break

    end_time = time.time()

    if detected_positions:
        if debug:
            print(f"Debug: {merchant_type.capitalize()} detected using {scan_method} at positions: {detected_positions} in {end_time - start_time:.2f} seconds")
        return detected_positions
    else:
        if debug:
            print(f"Debug: No {merchant_type.capitalize()} detected using {scan_method} on screen. Time taken: {end_time - start_time:.2f} seconds")
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


async def purchase_items(merchant_type, item_slots, bought_items, side, screen_width, screen_height, max_retries=4):
    """Helper function to handle item purchases with retry mechanism and dynamic ratio threshold."""

    for slot_name, (item_name, amount) in item_slots.items():
        if item_name == "None" or item_name in bought_items:
            continue

        print(f"Attempting to purchase item {item_name} from the {side} side with amount {amount}.")

        item_positions = None
        initial_ratio_threshold_ocr = 0.8
        
        for attempt in range(max_retries):
            current_ratio_threshold = initial_ratio_threshold_ocr - (0.05 * attempt)
            item_positions = await Merchant_Specific_Item_SCANNING_Process(
                merchant_type, item_name, threshold=0.75, ratio_threshold=current_ratio_threshold, ocr_double_check=False
            )
            if item_positions:
                break
            else:
                await asyncio.sleep(0.15)

        if not item_positions:
            print(f"Failed to detect item {item_name} after {max_retries} attempts. Skipping item.")
            continue

        detected_item_name, center_x, center_y = item_positions
        print(f"Detected {detected_item_name} at ({center_x}, {center_y}).")

        await asyncio.sleep(0.2)
        autoit.mouse_click(x=center_x, y=center_y)
        await asyncio.sleep(0.5)

        # Retry loop for double-checking the item shop name using OCR
        item_shop_name_positions = None
        
        
        for attempt in range(max_retries):
            current_ratio_threshold = initial_ratio_threshold_ocr - (0.05 * attempt)
            item_shop_name_positions = await Merchant_Specific_Item_SCANNING_Process(
                merchant_type, item_name, threshold=0.75, ratio_threshold=current_ratio_threshold, ocr_double_check=True
            )
            if item_shop_name_positions:
                print(f"Double-check successful for {item_name} on attempt {attempt + 1} with OCR.")
                break
            else:
                await asyncio.sleep(0.15)

        if not item_shop_name_positions:
            print(f"Failed to double-check item {item_name} after {max_retries} attempts. Skipping purchase.")
            continue

        # Perform button scanning to find purchase-related buttons
        purchase_amount_pos = convert_to_relative_coords(659, 603, screen_width, screen_height)
        purchase_button_pos = convert_to_relative_coords(702, 648, screen_width, screen_height)

        if purchase_amount_pos:
            autoit.mouse_click(x=purchase_amount_pos[0], y=purchase_amount_pos[1])
            autoit.send(str(amount))
            await asyncio.sleep(0.25)

        if purchase_button_pos:
            autoit.mouse_click(x=purchase_button_pos[0], y=purchase_button_pos[1])
            await asyncio.sleep(4)

        # Log the item as bought
        bought_items.add(item_name)
            
async def Merchant_Item_Buy_Process(merchant_type):
    """Process to purchase items from the merchant, while checking if the merchant is still present."""
    Merchant_screen_width, Merchant_screen_height = get_screen_resolution()
    config = load_config()
    merchant_item_slots = get_merchant_item_config_slots(config)
    bought_items = set()

    open_button_config = config.get("MERCHANT_OPEN_BUTTON_POSITION", [616, 883])
    open_button_pos = convert_to_relative_coords(open_button_config[0], open_button_config[1], Merchant_screen_width, Merchant_screen_height)
    
 
    autoit.mouse_click("left", open_button_pos[0], open_button_pos[1])
    
    # Step 1: Scroll down to the right side (where rare items should be)
    await asyncio.sleep(0.7)
    item_scroll_pos = convert_to_relative_coords(926, 720, Merchant_screen_width, Merchant_screen_height)
    
    autoit.mouse_move(item_scroll_pos[0], item_scroll_pos[1])
    autoit.mouse_wheel("up", 8)
    await asyncio.sleep(0.5)
    autoit.mouse_wheel("down", 2)
    await asyncio.sleep(0.4)
    autoit.mouse_move(item_scroll_pos[0] + 70, item_scroll_pos[1] + 70)
    await asyncio.sleep(0.3)

    # Send Merchant's Item Screenshot
    await Merchant_Items_Webhook_Sender(merchant_type, "")
    await purchase_items(merchant_type, merchant_item_slots[merchant_type], bought_items, "right", Merchant_screen_width, Merchant_screen_height)
    
    # Step 2: Scroll back up to the left side (common items)
    autoit.mouse_move(item_scroll_pos[0], item_scroll_pos[1])
    autoit.mouse_wheel("up", 8)
    await asyncio.sleep(0.4)
    autoit.mouse_move(item_scroll_pos[0] + 70, item_scroll_pos[1] + 70)
    await asyncio.sleep(0.5)

    # Send Merchant's Item Screenshot
    await purchase_items(merchant_type, merchant_item_slots[merchant_type], bought_items, "left", Merchant_screen_width, Merchant_screen_height)

    await merchant_reset_macro_phase()

async def merchant_reset_macro_phase():
    await asyncio.sleep(1.3)
    autoit.mouse_wheel("up", 15)
    await asyncio.sleep(1.2)
    autoit.mouse_wheel("down", 10)
    await asyncio.sleep(1.5)
    pydirectinput.press("F8")
 
       
async def send_webhook_notification(webhook_url, content, embed, merchant_face_image_binary=None, inventory_image_binary=None):
    form_data = aiohttp.FormData()

    if merchant_face_image_binary:
        form_data.add_field('file', merchant_face_image_binary, filename='epic_ss.png', content_type='image/png')
    
    if inventory_image_binary:
        form_data.add_field('file', inventory_image_binary, filename='inventory_ss.png', content_type='image/png')

    # payload to a JSON string
    payload_json = json.dumps({
        "content": content,
        "embeds": [embed.to_dict()]
    })

    form_data.add_field('payload_json', payload_json, content_type='application/json')

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, data=form_data) as response:
            if response.status == 204:
                print("Webhook sent successfully.")
            else: pass

async def Merchant_Webhook_Sender(Merchant_Name):
    """Sends a webhook message with a screenshot if a merchant is detected."""
    screenshot = take_screenshot()  # Merchant face screenshot
    webhook_urls = config.get("webhook_links", [])
    merchant_ps_link_enabled = config.get("merchant_ps_link_enabled", False)
    ps_link = config.get("merchant_private_server_link", "")
    ping_user_id = config.get(f"{Merchant_Name}_ping_userid", "")
    
    if screenshot:
        # Prepare the embed once
        embed = discord.Embed(
            title=f"{Merchant_Name.capitalize()} Detected!",
            description=f"{Merchant_Name.capitalize()} has been detected on your screen.",
            color=discord.Color.blue() if Merchant_Name == "mari" else discord.Color.purple()
        )
        
        # thumbnail based on the merchant
        thumbnail_url = (
            "https://static.wikia.nocookie.net/sol-rng/images/3/37/MARI_HIGH_QUALITYY.png/revision/latest?cb=20240704045119"
            if Merchant_Name == "mari" else
            "https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest?cb=20240630142936"
        )
        
        embed.add_field(name="Merchant Face Screenshot", value="", inline=False)
        embed.set_thumbnail(url=thumbnail_url)
        embed.set_image(url="attachment://epic_ss.png")  # Referencing the face screenshot
        embed.set_footer(text="Auto Merchant Detection")

        # Form the message content with a user ping
        message_content = f"<@{ping_user_id}> "
    
        if merchant_ps_link_enabled:
            message_content += f"{ps_link}"

        # Send the webhook notification for each URL
        for webhook_url in webhook_urls:
            try:
                merchant_image_binary = BytesIO()
                screenshot.save(merchant_image_binary, 'PNG')
                merchant_image_binary.seek(0)
                await send_webhook_notification(webhook_url, message_content, embed, merchant_face_image_binary=merchant_image_binary)
            except Exception as e:
                pass
            finally:
                merchant_image_binary.close()


async def Merchant_Items_Webhook_Sender(Merchant_Name, extra_info):
    """Sends a webhook message with a screenshot of the merchant's items."""
    screenshot = take_screenshot()
    webhook_urls = config.get("webhook_links", [])
    
    if screenshot:
        inventory_embed = discord.Embed(
            title=f"{Merchant_Name.capitalize()}'s Shop Items",
            description=f"{extra_info}",
            color=discord.Color.blue() if Merchant_Name == "mari" else discord.Color.purple()
        )
        
        inventory_embed.add_field(name="Item Screenshot", value="", inline=False)
        inventory_embed.set_image(url="attachment://inventory_ss.png")
        inventory_embed.set_footer(text="Auto Merchant Detection")

        # Send the webhook notification for each URL
        for webhook_url in webhook_urls:
            inventory_image_binary = BytesIO()
            screenshot.save(inventory_image_binary, 'PNG')
            inventory_image_binary.seek(0)

            await send_webhook_notification(webhook_url, "", inventory_embed, inventory_image_binary=inventory_image_binary)
            inventory_image_binary.close()
    else:
        print("Roblox window not found!")
        

@tasks.loop(seconds=2)
async def AUTO_MERCHANT_DETECTION_LOOP():
    """Automatically detect merchants and handle the item buying process."""
    global Merchant_ON_PROCESS_LOOP
    global merchant_cooldown_end_time

    try:
        current_time = time.time()
        
        # Check if cooldown period has expired
        if current_time < merchant_cooldown_end_time:
            return

        # Check if another process is already running
        if Merchant_ON_PROCESS_LOOP:
            return

        auto_merchant_detection = config.get('enable_auto_merchant', False)
        if not auto_merchant_detection:
            print("Auto merchant detection is disabled")
            return

        async with loop_lock:
            merchants = {
                'mari': False,
                'jester': False
            }

            tasks_list = []

            for merchant in merchants:
                positions = await Merchant_Headshot_Process(merchant)
                if positions:
                    print(f"{merchant.capitalize()} detected!")
                    
                    merchants[merchant] = True
                    Merchant_ON_PROCESS_LOOP = True
                    
                    await asyncio.sleep(4.5)
                    pydirectinput.press("F2")
                    await asyncio.sleep(0.5)
                    await activate_roblox_window()
                    await asyncio.sleep(2.8)
                    
                    # Create the tasks for webhook notification and item buying process
                    webhook_task = asyncio.create_task(Merchant_Webhook_Sender(merchant))
                    buy_process_task = asyncio.create_task(Merchant_Item_Buy_Process(merchant))

                    tasks_list.append(webhook_task)
                    tasks_list.append(buy_process_task)

            # Wait for all tasks to complete
            if tasks_list:
                try:
                    await asyncio.gather(*tasks_list)
                except Exception as e:
                    print(f"An error occurred during merchant processing: {e}")
                finally:
                    Merchant_ON_PROCESS_LOOP = False

                    if any(merchants.values()):
                        merchant_cooldown_end_time = current_time + 240

            # wait a little bit for the next loop
            if not any(merchants.values()):
                await asyncio.sleep(0.5)

    except Exception as e:
        print(f"Error in main merchant loop: {e}")
        
async def main():
    try:
        # Test calling the Merchant_Webhook_Sender
        # await asyncio.sleep(2)
        # await Merchant_Webhook_Sender("jester")
        # await Merchant_Items_Webhook_Sender("jester", "omg jester with oblivion 😳 ??!")
        AUTO_MERCHANT_DETECTION_LOOP.start()
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the detection loop...")
        AUTO_MERCHANT_DETECTION_LOOP.stop()  # Stops the loop 
    finally:
        print("Program terminated.")

if __name__ == "__main__":
    try:
        print("Merchant feature is running in background...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Merchant feature interrupted by user (Ctrl + C pressed)")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        print("Program terminated.")

""" MERCHANT FEATURE """

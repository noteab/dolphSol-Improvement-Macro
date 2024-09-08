import subprocess
import importlib.util
import os
import webbrowser
import sys
import json

# List of required modules
all_required_modules = [
    'discord', 'python-dotenv', 'pyautoit', 'pygetwindow', 'Pillow', 'psutil',
    'pywin32', 'pypiwin32', 'pytesseract', 'opencv-python', 'numpy', 
    'pyautogui', 'icecream', 'requests', 'pytest-shutil', 'fuzzywuzzy', 'pynput', 'pydirectinput'
]

# Path to detect if setup has already run
setup_status_file = "settings/setup_status.json"
tesseract_setup_file = "tesseract-ocr-w64-setup-5.4.0.20240606.exe"

# Next Page
def next_page():
    for i in range(100):
        print()

# Function to check if a module is installed
def check_module_installed(module_name):
    return importlib.util.find_spec(module_name) is not None

# Function to install missing modules
def install_modules(missing_modules):
    print(f"Installing missing modules: {', '.join(missing_modules)}")
    subprocess.call([sys.executable, "-m", "pip", "install", *missing_modules])

# Function to uninstall modules
def uninstall_modules():
    for module in all_required_modules:
        print(f"Uninstalling {module}...")
        subprocess.call([sys.executable, "-m", "pip", "uninstall", module, "-y"])

# Function to check if Tesseract is installed
def check_tesseract_installed():
    try:
        subprocess.run(["tesseract", "-v"], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return os.path.isdir("/Program Files/Tesseract-OCR")

# Function to run the Tesseract installer or prompt the user to manually run it
def run_tesseract_installer():
    if os.path.exists(tesseract_setup_file):
        print(f"Running {tesseract_setup_file}...")
        subprocess.call([tesseract_setup_file])
    else:
        print(f"{tesseract_setup_file} not found. Please download the installer in the same directory as this program.")
        input("Press Enter to download the installer.")
        webbrowser.open("https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe")
        input("After downloading the file, place it in the same directory as this program and press Enter to continue.")

# Function to check modules and offer to install Tesseract if needed
def check_modules_and_tesseract(modules_to_install=None):
    next_page()
    if modules_to_install is None:
        modules_to_install = all_required_modules
    
    missing_modules = [module for module in modules_to_install if not check_module_installed(module)]
    
    if missing_modules:
        print(f"Missing modules: {', '.join(missing_modules)}")
        user_input = input("Would you like to install the missing modules? (y/n): ").strip().lower()
        if user_input == 'y':
            install_modules(missing_modules)
        else:
            print("Skipping module installation.")

    next_page()
    if not check_tesseract_installed():
        user_input = input("Tesseract is not installed. Would you like to install it? (y/n): ").strip().lower()
        if user_input == 'y':
            run_tesseract_installer()
        else:
            print("Skipping Tesseract installation.")
    else:
        print("All required modules and Tesseract are installed!")
    input("\nPress Enter to continue.")

# Function to guide through merchant detection setup
def merchant_detection_setup():
    next_page()
    print("\nThis program has a merchant detection feature named `merchant_main` and `merchant_gui_setting`.")
    user_input = input("Would you like to use it? (y/n): ").strip().lower()

    if user_input == 'y':
        next_page()
        print("\nOpening Discord Developer Applications page...")
        webbrowser.open("https://discord.com/developers/applications")
        print("Create a new application, choose a name, and go to the 'Bot' section to copy the bot token.")
        print("Paste the bot token into a new Notepad file.")
        input("\nPress Enter when you are done.")

        next_page()
        print("\nRefer to this page for adding required permissions to your bot:")
        webbrowser.open("https://wiki.botdesignerdiscord.com/resources/permissions.html")
        input("Press Enter after reviewing the permissions and adding them to your bot.")

        next_page()
        print("\nNext, copy your Discord user ID and channel ID and paste them into the same Notepad.")
        webbrowser.open("https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID")
        input("Press Enter once you have copied and saved your user and channel IDs.")

        next_page()
        print("\nOpen `PYTHON_SETTINGS_GUI.py`, go to the bot section, and paste the required fields (bot token, user ID, channel ID).")
        print("After that, press 'Update Bot Info' in the script.")
        subprocess.call([sys.executable, os.path.join(os.path.dirname(__file__), "Python_Settings_GUI.pyw")])
        input("\nPress Enter when you are done with this step.")

        next_page()
        print("\nNow opening `discord_cmd.py` to complete the setup.")
        subprocess.call([sys.executable, os.path.join(os.path.dirname(__file__),"settings/discord_cmd.py")])

        input("\nIs the setup complete? (y/n): ").strip().lower()
        print("Setup is complete!")

# Function to check if setup was previously completed
def check_previous_setup():
    if os.path.exists(setup_status_file):
        with open(setup_status_file, 'r') as f:
            status = json.load(f)
        return status.get("setup_complete", False)
    return False

# Function to mark setup as completed
def mark_setup_complete():
    with open(setup_status_file, 'w') as f:
        json.dump({"setup_complete": True}, f)

# Main prompt
def main():
    print("Welcome to the setup script!")
    user_input = input("Would you like to perform a normal installation, express installation, customize installation or uninstall the program? (normal/express/uninstall): ").strip().lower()
    
    if user_input == 'customize':
        modules_to_install = input(f"Enter the modules to install from the following list (comma-separated): {', '.join(all_required_modules)}: ").strip().split(',')
        modules_to_install = [module.strip() for module in modules_to_install]

        print("Warning: This feature is for testing purposes. The program may not work properly without all necessary modules.")
        user_input = input("Do you want to proceed with installing only the selected modules? (y/n): ").strip().lower()
        
        if user_input == 'y':
            check_modules_and_tesseract(modules_to_install)
        else:
            print("Proceeding with full installation.")
            check_modules_and_tesseract()

    elif user_input == 'express':
        print("Performing express installation...")
        check_modules_and_tesseract()
        next_page()
        print("Skipping merchant setup.")
        user_input = input("Do you want to run `discord_cmd.py` now? (y/n): ").strip().lower()
        if user_input == 'y':
            subprocess.call([sys.executable, os.path.join(os.path.dirname(__file__),"settings/discord_cmd.py")])
        print("Setup is complete.")
        input()
        return

    elif user_input == 'uninstall':
        uninstall_modules()
        run_tesseract_installer()
        print("Uninstall process is complete.")
        return

    elif user_input == 'normal':
        print("Performing normal installation...")
        check_modules_and_tesseract()
        # Proceed with merchant detection setup
        merchant_detection_setup()
        # Mark setup as complete
        mark_setup_complete()
        
        return

    else:
        print("Invalid option selected. Exiting.")
        return


if __name__ == "__main__":
    main()

import subprocess
import importlib.util
import os
import webbrowser
import sys
import json
import shutil
import pkg_resources

# List of required modules
all_required_modules = [
    'discord', 'python-dotenv', 'pyautoit', 'keyboard', 'pygetwindow', 'Pillow', 'psutil',
    'pywin32', 'pypiwin32', 'pytesseract', 'opencv-python', 'numpy', 
    'pyautogui', 'icecream', 'requests', 'pytest-shutil', 'pystray', 'fuzzywuzzy', 'pynput', 'pydirectinput'
]

# Path to detect if setup has already run
setup_status_file = "setup_status.json"
tesseract_setup_file = "tesseract-ocr-w64-setup-5.4.0.20240606.exe"
directory_file = "directory_path.json"

# Function to check if a module is installed
def check_module_installed(module_name):
    try:
        pkg_resources.get_distribution(module_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

# Function to install missing modules
def install_modules(missing_modules):
    print(f"\nInstalling missing modules: {', '.join(missing_modules)}")
    subprocess.call([sys.executable, "-m", "pip", "install", *missing_modules])

# Function to uninstall modules
def uninstall_modules():
    for module in all_required_modules:
        print(f"\nUninstalling {module}...")
        subprocess.call([sys.executable, "-m", "pip", "uninstall", module, "-y"])

# Function to check if Tesseract is installed
def check_tesseract_installed():
    try:
        subprocess.run(["tesseract", "-v"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    tesseract_dir = "C:/Program Files/Tesseract-OCR"
    return os.path.isdir(tesseract_dir)

# Function to run the Tesseract installer or prompt the user to manually run it
def run_tesseract_installer():
    if os.path.exists(tesseract_setup_file):
        print(f"\nRunning {tesseract_setup_file}...")
        subprocess.call([tesseract_setup_file])
    else:
        print(f"\n{tesseract_setup_file} not found.")
        input("Please download the installer from the following link: https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe")
        input("Place it in the same directory as this program and press Enter to continue.")

# Function to check modules and offer to install Tesseract if needed
def check_modules_and_tesseract():
    missing_modules = [module for module in all_required_modules if not check_module_installed(module)]
    
    if missing_modules:
        print(f"\nMissing modules: {', '.join(missing_modules)}")
        user_input = input("Would you like to install the missing modules? (y/n): ").strip().lower()
        if user_input == 'y':
            install_modules(missing_modules)
        else:
            print("Skipping module installation.")

    if not check_tesseract_installed():
        user_input = input("Tesseract is not installed. Would you like to install it? (y/n): ").strip().lower()
        if user_input == 'y':
            run_tesseract_installer()
        else:
            print("Skipping Tesseract installation.")
    else:
        print("All required modules and Tesseract are installed!")

# Function to guide through merchant detection setup
def merchant_detection_setup():
    print("\nThis program has a merchant detection feature named `merchant_main` and `merchant_gui_setting`.")
    user_input = input("Would you like to use it? (y/n): ").strip().lower()

    if user_input == 'y':
        print("\nOpening Discord Developer Applications page...")
        webbrowser.open("https://discord.com/developers/applications")
        input("Create a new application, choose a name, and go to the 'Bot' section to copy the bot token.")
        input("Paste the bot token into a new Notepad file and press Enter when you are done.")

        print("\nRefer to this page for adding required permissions to your bot:")
        webbrowser.open("https://wiki.botdesignerdiscord.com/resources/permissions.html")
        input("Press Enter after reviewing the permissions and adding them to your bot.")

        print("\nNext, copy your Discord user ID and channel ID and paste them into the same Notepad.")
        webbrowser.open("https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID")
        input("Press Enter once you have copied and saved your user and channel IDs.")

        print("\nOpen `PYTHON_GUI_SETTING.py`, go to the bot section, and paste the required fields (bot token, user ID, channel ID).")
        input("After that, press 'Update Bot Info' in the script and press Enter when you are done with this step.")

        print("\nNow opening `discord_cmd.py` to complete the setup.")
        subprocess.call([sys.executable, "discord_cmd.py"])

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

# Function to save the folder path where the script is located
def save_directory_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(directory_file, 'w') as f:
        json.dump({"directory_path": script_dir}, f)

# Function to delete the saved folder path
def delete_saved_directory():
    if os.path.exists(directory_file):
        with open(directory_file, 'r') as f:
            data = json.load(f)
        folder_to_delete = data.get("directory_path")
        if folder_to_delete and os.path.exists(folder_to_delete):
            print(f"\nDeleting folder: {folder_to_delete}")
            shutil.rmtree(folder_to_delete)
        else:
            print(f"\nFolder not found: {folder_to_delete}")

# Function to handle Tesseract uninstallation
def uninstall_tesseract():
    if check_tesseract_installed():
        # This part assumes there's an uninstaller available; modify if needed
        print("\nUninstalling Tesseract...")
        # Replace the following with the actual uninstall command if available
        # subprocess.call(["uninstall_tesseract_command"])
    else:
        print("\nTesseract installer not found.")
        user_input = input("Please place the Tesseract installer in the same directory and run this program again, or choose to uninstall manually. (y for run again, n for manual): ").strip().lower()
        if user_input == 'y':
            print("Please place the Tesseract installer in the directory and run this program again.")
            sys.exit()
        else:
            print("Proceeding to manual uninstallation.")

# Function to handle complete uninstallation
def uninstall():
    uninstall_modules()
    uninstall_tesseract()  # Handle Tesseract uninstallation

    user_input = input("\nAfter uninstalling all modules and Tesseract, would you like to completely uninstall the folder where this program is located? (y/n): ").strip().lower()
    if user_input == 'y':
        delete_saved_directory()
        print("Folder has been deleted.")
    else:
        print("Skipping folder deletion. Exiting program.")

# Main prompt
def main():
    if not os.path.exists(directory_file):
        save_directory_path()
    
    print("Welcome to the setup script!")
    user_input = input("Select installation type (normal/express/customize/uninstall): ").strip().lower()
    
    if user_input == 'customize':
        modules_to_install = input(f"Enter the modules to install from the following list (comma-separated): {', '.join(all_required_modules)}: ").strip().split(',')
        modules_to_install = [module.strip() for module in modules_to_install]

        print("Warning: This feature is for testing purposes. The program may not work properly without all necessary modules.")
        user_input = input("Proceed with installing only the selected modules? (y/n): ").strip().lower()
        
        if user_input == 'y':
            check_modules_and_tesseract()
        else:
            print("Proceeding with full installation.")
            check_modules_and_tesseract()

    elif user_input == 'express':
        print("Performing express installation...")
        check_modules_and_tesseract()
        print("Skipping merchant setup.")
        user_input = input("Run `discord_cmd.py` now? (y/n): ").strip().lower()
        if user_input == 'y':
            subprocess.call([sys.executable, "discord_cmd.py"])
        print("Setup is complete.")
        return

    elif user_input == 'uninstall':
        uninstall()
        return

    elif user_input == 'normal':
        print("Performing normal installation...")
        check_modules_and_tesseract()
        merchant_detection_setup()
        mark_setup_complete()
        return

    else:
        print("Invalid option selected. Exiting.")
        return

if __name__ == "__main__":
    main()

import os
import subprocess
import sys
import json
import ctypes
import pathlib

sys.dont_write_bytecode = True

# Define required packages
REQUIRED_MODULES = ['customtkinter', 'easyocr','py-cord']

def install_module(module):
    """Install a Python module using pip."""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])

def check_and_install_modules():
    """Check and install required modules."""
    for module in REQUIRED_MODULES:
        try:
            __import__(module)
        except ImportError:
            print(f"Installing {module}...")
            install_module(module)

def download_easyocr_model():
    """Run a basic EasyOCR script to download the recognition model."""
    import easyocr

    reader = easyocr.Reader(['en'])  # Create a reader instance
    print("EasyOCR model downloaded successfully.")

def run_update_checker():
    """Run the update checker"""
    # try:
    from data.update_checker import update_checker
    # except ImportError:
    #     ctypes.windll.user32.MessageBoxW(0, "UPDATE CHECKER NOT FOUND", "Error", 0)
    update_checker.check_for_updates()
    

def create_main_gui():
    """Run the main GUI script."""
    try:
        from data.main_gui import main_gui
    except ImportError:
        ctypes.windll.user32.MessageBoxW(0, "MAIN GUI NOT FOUND", "Error", 0)

    main_gui.MainWindow().mainloop()

def set_path():
    try: 
        from data.lib import config
    except ImportError:
        ctypes.windll.user32.MessageBoxW(0, "CONFIG FILE NOT FOUND", "Error", 0)
    config.set_path(pathlib.Path(__file__).parent.resolve())


def main():
    # check_and_install_modules()
    # """Main function to check if it's the first time running the installer."""
    # if not os.path.exists('data/installer_status.json'):
    #     download_easyocr_model()
    #     # Create a file to indicate the installation has occurred
    #     with open('data/installer_status.json', 'w') as f:
    #         json.dump({"installed": True}, f)
    set_path()
    run_update_checker()
    create_main_gui()


if __name__ == "__main__":
    main()

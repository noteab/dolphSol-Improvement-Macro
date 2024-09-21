import os
import subprocess
import sys
import json

# Define required packages
REQUIRED_MODULES = ['ctk', 'easyocr','py-cord']

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

def create_main_gui():
    """Run the main GUI script."""
    main_gui_path = os.path.join('data', 'main_gui', 'main_gui.py')
    if os.path.exists(main_gui_path):
        subprocess.Popen([sys.executable, main_gui_path])
        print("Main GUI has been launched.")
    else:
        print("Main GUI script not found.")

def uninstall_modules():
    """Uninstall the required modules."""
    for module in REQUIRED_MODULES:
        print(f"Uninstalling {module}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', module])

def first_time_setup():
    """Run the first-time setup."""
    print("Hi! Welcome to the dSIM 2.0 installer.")
    installation_type = input("Would you like an express or normal installation? (e/n): ").strip().lower()

    if installation_type == 'n':
        check_and_install_modules()
        download_easyocr_model()
    elif installation_type == 'e':
        print("Express installation will skip module checks.")
        download_easyocr_model()
    else:
        print("Invalid option selected. Exiting installer.")
        sys.exit(1)

    create_main_gui()

def subsequent_setup():
    """Handle subsequent installs or uninstall."""
    print("Welcome back to the dSIM 2.0 installer.")
    action = input("Would you like to (i)nstall, (u)ninstall, or (e)xpress install? (i/u/e): ").strip().lower()

    if action == 'i':
        check_and_install_modules()
        download_easyocr_model()
    elif action == 'e':
        print("Express installation will skip module checks.")
        download_easyocr_model()
    elif action == 'u':
        uninstall_modules()
        print("Uninstallation complete.")
        sys.exit(0)
    else:
        print("Invalid option selected. Exiting installer.")
        sys.exit(1)

    create_main_gui()

def main():
    """Main function to check if it's the first time running the installer."""
    if not os.path.exists('installer_status.json'):
        first_time_setup()
        # Create a file to indicate the installation has occurred
        with open('installer_status.json', 'w') as f:
            json.dump({"installed": True}, f)
    else:
        subsequent_setup()

if __name__ == "__main__":
    main()

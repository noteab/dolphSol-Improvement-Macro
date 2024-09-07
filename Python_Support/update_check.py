import os
import requests
from zipfile import ZipFile
from io import BytesIO
import shutil
import tempfile
import time
from tkinter import Tk, filedialog, messagebox

# Define constants and file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/Noteab-Improvement/Python_Support/VERSION.txt"
ZIP_DOWNLOAD_URL = "https://github.com/noteab/dolphSol-Improvement-Macro/archive/refs/heads/Noteab-Improvement.zip"
LOCAL_VERSION_FILE = os.path.join(BASE_DIR, "VERSION.txt")
MAIN_AHK_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/Noteab-Improvement/Main.ahk"
LOCAL_MAIN_AHK_PATH = os.path.join(BASE_DIR, "..", "Main.ahk")  # Path to Main.ahk outside Python_Support
FILES_TO_KEEP = {".env", "config.json"}  # Set of filenames to preserve
CHANGELOG_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/Noteab-Improvement/CHANGELOG.md"
CHANGES_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/Noteab-Improvement/CHANGES.md"

def extract_version(content):
    """Extract version number from content."""
    try:
        version_line = content.split('=')[1].strip().strip('"')
        return version_line
    except IndexError:
        raise Exception("Failed to parse version content")

def get_github_version():
    """Fetch the latest version number from GitHub."""
    response = requests.get(GITHUB_VERSION_URL)
    if response.status_code == 200:
        return extract_version(response.text)
    else:
        raise Exception("Failed to fetch version from GitHub")

def get_local_version():
    """Get the local version number."""
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, 'r') as file:
            return extract_version(file.read())
    else:
        return None

def download_main_ahk(output_folder=None):
    """Download and save the Main.ahk file."""
    try:
        response = requests.get(MAIN_AHK_URL)
        if response.status_code == 200:
            if output_folder:
                ahk_path = os.path.join(output_folder, "Main.ahk")
            else:
                ahk_path = LOCAL_MAIN_AHK_PATH
            with open(ahk_path, 'wb') as file:
                file.write(response.content)
            print("Main.ahk updated successfully!")
        else:
            raise Exception("Failed to download Main.ahk from GitHub")
    except Exception as e:
        print(f"An error occurred while updating Main.ahk: {e}")
        import traceback
        traceback.print_exc()

def download_changelog():
    """Download and display the changelog."""
    try:
        response = requests.get(CHANGELOG_URL)
        if response.status_code == 200:
            print("\n--- Changelog ---")
            print(response.text)
            print("------------------\n")
        else:
            print("Failed to fetch changelog from GitHub")
    except Exception as e:
        print(f"An error occurred while fetching the changelog: {e}")
        import traceback
        traceback.print_exc()

def download_changes():
    """Download and display the changes."""
    try:
        response = requests.get(CHANGES_URL)
        if response.status_code == 200:
            print("\n--- Changes ---")
            print(response.text)
            print("------------------\n")
        else:
            print("Failed to fetch changes from GitHub")
    except Exception as e:
        print(f"An error occurred while fetching the changes: {e}")
        import traceback
        traceback.print_exc()

def download_update(output_folder=None):
    """Download and apply the update to a specified folder."""
    try:
        response = requests.get(ZIP_DOWNLOAD_URL)
        if response.status_code == 200:
            zip_file = ZipFile(BytesIO(response.content))
            
            # Determine extraction path
            if not output_folder:
                output_folder = BASE_DIR
            
            # Extract to a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_file.extractall(temp_dir)
                
                extracted_folder_name = zip_file.namelist()[0].split('/')[0]
                extracted_python_support = os.path.join(temp_dir, extracted_folder_name, "Python_Support")
                
                if not os.path.exists(extracted_python_support):
                    print(f"Path {extracted_python_support} does not exist. Aborting update.")
                    time.sleep(4)
                    return
                
                # Overwrite the current Python_Support directory files
                for root, dirs, files in os.walk(extracted_python_support):
                    relative_path = os.path.relpath(root, extracted_python_support)
                    destination_dir = os.path.join(output_folder, relative_path)

                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)

                    for file in files:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(destination_dir, file)
                        if os.path.basename(file) in FILES_TO_KEEP and os.path.exists(dest_file):
                            continue
                        shutil.copy2(src_file, dest_file)
                
                print("Update applied directly to the specified folder.")
                time.sleep(4)
                
                # Download and update the Main.ahk file
                download_main_ahk(output_folder)
        
        else:
            raise Exception("Failed to download the latest version from GitHub")
    
    except Exception as e:
        print(f"An error occurred during the update process: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(10)

def prompt_for_output_folder():
    """Prompt user to select an output folder."""
    root = Tk()
    root.withdraw()  # Hide the main window
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        messagebox.showwarning("Warning", "No folder selected. Update will not proceed.")
    return output_folder

def prompt_for_update_action():
    """Prompt user to choose update action."""
    root = Tk()
    root.withdraw()  # Hide the main window
    action = messagebox.askquestion("Update Options", "Do you want to:\n1.(Press YES FOR THIS) Download the changes into a desired output folder?\n2. (PRESS NO FOR THIS)Replace the changes normally?")
    return action

def check_for_updates():
    """Check for updates and handle reinstallation prompt."""
    try:
        github_version = get_github_version()
        local_version = get_local_version()

        if local_version != github_version:
            print(f"New version available: {github_version}. Preparing the update...")
            action = prompt_for_update_action()
            if action == 'yes':  # Download changes into a desired output folder
                output_folder = prompt_for_output_folder()
                if output_folder:
                    download_update(output_folder)
                    download_changes()
                else:
                    print("Reinstallation canceled.")
            else:  # Replace changes normally
                download_update()
                download_changes()
        else:
            print("Already up-to-date.")
            time.sleep(4)
            # Show changes even if up-to-date
            download_changes()
            # Prompt user to reinstall the latest version
            root = Tk()
            root.withdraw()  # Hide the main window
            if messagebox.askyesno("Reinstall", "Do you want to reinstall the latest version of the program?"):
                action = prompt_for_update_action()
                if action == 'yes':  # Download changes into a desired output folder
                    output_folder = prompt_for_output_folder()
                    if output_folder:
                        download_update(output_folder)
                        download_changes()
                    else:
                        print("Reinstallation canceled.")
                else:  # Replace changes normally
                    download_update()
                    download_changes()
    
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

# Run the update check
check_for_updates()
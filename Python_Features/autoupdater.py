import os
import requests
from zipfile import ZipFile
from io import BytesIO
import shutil
import tempfile
import time
from tkinter import Tk, Button, filedialog, messagebox

# Define constants and file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/Noteab-Improvement/Python_Features/data/VERSION.txt"
ZIP_DOWNLOAD_URL = "https://github.com/noteab/dolphSol-Improvement-Macro/archive/refs/heads/Noteab-Improvement.zip"
LOCAL_VERSION_FILE = os.path.join(BASE_DIR, "data/VERSION.txt")
MAIN_AHK_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/Noteab-Improvement/Main.ahk"
LOCAL_MAIN_AHK_PATH = os.path.join(BASE_DIR, "..", "Main.ahk")  # Path to Main.ahk outside Python_Features
FILES_TO_KEEP = {"data/.env", "data/config.json"}  # Set of filenames to preserve
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
    updated_files = []
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
                extracted_python_features = os.path.join(temp_dir, extracted_folder_name, "Python_Features")
                
                if not os.path.exists(extracted_python_features):
                    print(f"Path {extracted_python_features} does not exist. Aborting update.")
                    time.sleep(4)
                    return updated_files
                
                # Overwrite the current Python_Features directory files
                for root, dirs, files in os.walk(extracted_python_features):
                    relative_path = os.path.relpath(root, extracted_python_features)
                    destination_dir = os.path.join(output_folder, relative_path)

                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)

                    for file in files:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(destination_dir, file)
                        if os.path.basename(file) in FILES_TO_KEEP and os.path.exists(dest_file):
                            continue
                        shutil.copy2(src_file, dest_file)
                        updated_files.append(dest_file)
                
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
    
    return updated_files

def prompt_for_output_folder():
    """Prompt user to select an output folder."""
    root = Tk()
    root.withdraw()  # Hide the main window
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    return output_folder

def handle_desired_output_folder(root):
    """Handle the 'Desired Output Folder' button action."""
    output_folder = prompt_for_output_folder()
    if output_folder:
        updated_files = download_update(output_folder)
        download_changes()
        print("\nUpdated files:")
        for file in updated_files:
            print(file)
    else:
        print("Reinstallation canceled.")
    root.destroy()

def handle_automatic_update(root):
    """Handle the 'Automatic Update' button action."""
    updated_files = download_update()
    download_changes()
    print("\nUpdated files:")
    for file in updated_files:
        print(file)
    root.destroy()

def create_update_gui():
    """Create the GUI for update options."""
    root = Tk()
    root.title("Update Options")

    Button(root, text="Desired Output Folder", command=lambda: handle_desired_output_folder(root)).pack(pady=10)
    Button(root, text="Automatic Update", command=lambda: handle_automatic_update(root)).pack(pady=10)

    root.mainloop()

def check_for_updates():
    """Check for updates and handle reinstallation prompt."""
    try:
        github_version = get_github_version()
        local_version = get_local_version()

        if local_version != github_version:
            print(f"New version available: {github_version}. Preparing the update...")
            create_update_gui()
        else:
            print("Already up-to-date.")
            time.sleep(4)
            # Show changes even if up-to-date
            download_changes()
            # Prompt user to reinstall the latest version
            root = Tk()
            root.withdraw()  # Hide the main window
            if messagebox.askyesno("Reinstall", "Do you want to reinstall the latest version of the program?"):
                create_update_gui()
    
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

# Run the update check
check_for_updates()
input()

import os
import requests
from zipfile import ZipFile
from io import BytesIO
import shutil
import tempfile
import time

""" GITHUB UPDATE NOTIFIER """
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/Noteab-Improvement/Python_Support/VERSION.txt"
ZIP_DOWNLOAD_URL = "https://github.com/noteab/dolphSol-Improvement-Macro/archive/refs/heads/Noteab-Improvement.zip"
LOCAL_VERSION_FILE = os.path.join(BASE_DIR, "VERSION.txt")
MAIN_AHK_URL = "https://raw.githubusercontent.com/noteab/dolphSol-Improvement-Macro/Noteab-Improvement/Main.ahk"
LOCAL_MAIN_AHK_PATH = os.path.join(BASE_DIR, "..", "Main.ahk")  # Path to Main.ahk outside Python_Support
EXTRACT_PATH = BASE_DIR
FILES_TO_KEEP = {".env"}  # Set of filenames to preserve

def extract_version(content):
    try:
        version_line = content.split('=')[1].strip().strip('"')
        return version_line
    except IndexError:
        raise Exception("Failed to parse version content")

# Function to get the latest version from GitHub
def get_github_version():
    response = requests.get(GITHUB_VERSION_URL)
    if response.status_code == 200:
        return extract_version(response.text)
    else:
        raise Exception("Failed to fetch version from GitHub")

# Function to get the local version
def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, 'r') as file:
            return extract_version(file.read())
    else:
        return None

def download_main_ahk():
    try:
        response = requests.get(MAIN_AHK_URL)
        if response.status_code == 200:
            with open(LOCAL_MAIN_AHK_PATH, 'wb') as file:
                file.write(response.content)
            print("Main.ahk updated successfully!")
        else:
            raise Exception("Failed to download Main.ahk from GitHub")
    except Exception as e:
        print(f"An error occurred while updating Main.ahk: {e}")
        import traceback
        traceback.print_exc()

def download_update():
    try:
        response = requests.get(ZIP_DOWNLOAD_URL)
        if response.status_code == 200:
            zip_file = ZipFile(BytesIO(response.content))
            
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
                    destination_dir = os.path.join(EXTRACT_PATH, relative_path)

                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)

                    for file in files:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(destination_dir, file)
                        if os.path.basename(file) in FILES_TO_KEEP and os.path.exists(dest_file):
                            continue
                        shutil.copy2(src_file, dest_file)
                
                print("Update applied directly to the current Python_Support folder.")
                time.sleep(4)
                
                # Download and update the Main.ahk file
                download_main_ahk()
        
        else:
            raise Exception("Failed to download the latest version from GitHub")
    
    except Exception as e:
        print(f"An error occurred during the update process: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(10)

def check_for_updates():
    try:
        github_version = get_github_version()
        local_version = get_local_version()

        if local_version != github_version:
            print(f"New version available: {github_version}. Preparing the update...")
            download_update()
        else:
            print("Already up-to-date.")
            time.sleep(4)
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

check_for_updates()
""" GITHUB UPDATE NOTIFIER """

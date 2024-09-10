import subprocess
import sys

# List of required packages
required_packages = [
    "setuptools", "subprocess", "importlib", "os", "webbrowser", 
    "json", "shutil", "pkg_resources", "dotenv"
]

def install(package):
    """Helper function to install a package via pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

def check_and_install_modules():
    """Check if the required packages are installed, and install them if necessary."""
    for package in required_packages:
        try:
            if package == "subprocess":
                # subprocess is a built-in module, no need to install
                continue
            if package == "importlib":
                # importlib is part of the Python standard library, no need to install
                continue
            # Check if the package is already installed
            __import__(package)
            print(f"{package} is already installed.")
        except ImportError:
            print(f"{package} is not installed. Installing...")
            install(package)
            print(f"{package} has been installed.")

def main():
    print("Installing required modules via pip...")

    # Install the required modules
    try:
        check_and_install_modules()
        print("All required modules installed!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
        sys.exit(1)

    # Run Installer.py
    print("\nNow running Installer.py to finish the installation.")
    try:
        subprocess.run([sys.executable, "installer.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run Installer.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
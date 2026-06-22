import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

# Official Google Minimal Platform Tools URL (Windows)
ADB_ZIP_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
LOCAL_ADB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "bin", "adb"))
LOCAL_ADB_PATH = os.path.join(LOCAL_ADB_DIR, "adb.exe")

def is_adb_functional(adb_path):
    """Check if the given adb path can run and execute properly."""
    try:
        # Run adb version to check functionality
        result = subprocess.run([adb_path, "version"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            return True
    except Exception:
        pass
    return False

def get_or_download_adb(configured_path="adb", log_fn=print):
    """
    Checks if a working ADB exists (configured path, system path, or local path).
    If not, downloads and extracts the official Windows binary from Google.
    Returns the valid path to adb.exe or None if it fails.
    """
    # 1. Check if configured_path (e.g. 'adb') works in system environment
    if is_adb_functional(configured_path):
        log_fn(f"Using system-wide ADB: '{configured_path}'")
        return configured_path

    # 2. Check if local ADB is already downloaded and working
    if is_adb_functional(LOCAL_ADB_PATH):
        log_fn(f"Using local ADB instance at: '{LOCAL_ADB_PATH}'")
        return LOCAL_ADB_PATH

    # 3. Download ADB if not found
    log_fn("ADB was not found on your system. Downloading minimal ADB package from Google...")
    
    try:
        # Create directory
        os.makedirs(LOCAL_ADB_DIR, exist_ok=True)
        
        # Download platform-tools zip
        zip_path = os.path.join(LOCAL_ADB_DIR, "platform-tools.zip")
        log_fn(f"Downloading from: {ADB_ZIP_URL}")
        
        # Download file
        urllib.request.urlretrieve(ADB_ZIP_URL, zip_path)
        log_fn("Download complete. Extracting platform-tools...")

        # Extract only the necessary files for ADB to work
        required_files = ["adb.exe", "AdbWinApi.dll", "AdbWinInterface.dll"]
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                filename = os.path.basename(member)
                if filename in required_files:
                    # Extract directly to bin/adb/
                    source = zip_ref.open(member)
                    target_path = os.path.join(LOCAL_ADB_DIR, filename)
                    with open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)
                    log_fn(f"Extracted: {filename}")
        
        # Remove zip file after extraction
        try:
            os.remove(zip_path)
        except Exception:
            pass

        # Verify functionality of downloaded file
        if is_adb_functional(LOCAL_ADB_PATH):
            log_fn(f"Local ADB successfully installed and verified at: '{LOCAL_ADB_PATH}'")
            return LOCAL_ADB_PATH
        else:
            log_fn("Error: Local ADB was downloaded but could not be verified.")
            return None

    except Exception as e:
        log_fn(f"Failed to automatically download ADB: {e}")
        return None

def get_connected_devices(adb_path):
    """
    Executes 'adb devices' and returns a list of connected device IDs.
    """
    try:
        result = subprocess.run([adb_path, "devices"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            devices = []
            for line in lines[1:]: # Skip the first line: "List of devices attached"
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
            return devices
    except Exception:
        pass
    return []

if __name__ == "__main__":
    print("Testing ADB Helper...")
    path = get_or_download_adb()
    if path:
        print(f"ADB is ready at: {path}")
        devices = get_connected_devices(path)
        print(f"Connected devices: {devices}")
    else:
        print("ADB could not be obtained.")

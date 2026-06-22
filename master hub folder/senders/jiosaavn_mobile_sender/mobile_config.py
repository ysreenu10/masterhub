# Configuration for EEG Music Control System

# Target Selection: 'pc' (controls PC web browser) or 'mobile' (controls JioSaavn Android app)
CONTROL_TARGET = "mobile"

# ADB Configuration (Only used when CONTROL_TARGET is 'mobile')
ADB_PATH = "adb"            # Executable name or absolute path. Will default to local download if not found.
ADB_DEVICE_ID = None        # Set to specific device serial if multiple devices are plugged in

# Emotiv Cortex API Credentials
JIOSAAVN_URL = "https://www.jiosaavn.com/"
NEW_RELEASES_URL = "https://www.jiosaavn.com/new-releases"
CLIENT_ID = "9i4W3CpFRFmX9MprESsIq87jpkidIYzJLlbNQmqF"
CLIENT_SECRET = "QSkbEhyNjxLO7AuUGRXiiNQyff3AnkaZB9Jyjh5lHU1KsAv4NqLsWN45qLUOzbb2eKqo2yrCbAP7Rtav2X0OYJNZ9P0u89j38MIBJzIObC8s96Ux9iF3DSfHdsLnUQK4"

# Command Thresholds
CONFIDENCE_THRESHOLD = 0.5  # Increased to avoid accidental triggers
# DEBOUNCE_TIME = 2.0        # 3 seconds between actions to slow it down
DEBOUNCE_TIME = 0.3
# Command Mapping
# Options: 'playpause', 'prevtrack', 'nexttrack', 'volumeup', 'volumedown', 'home', 'search'
COMMAND_MAP = { 
    "push": "play/pause",
    "left": "prevtrack",
    "right": "nexttrack",
    "pull": "volumeup",
    "lift": "volumedown",
    "pop": "home",
    "think": "search"
}

# Search options for the think command
SEARCH_TERMS = [
    "Telugu Popular Songs",
    "Pawan Kalyan Hits",
    "Bahubali Songs",
    "Allu Arjun Songs",
    "Mahesh Babu Hits",
    "NTR Songs",
    "Anirudh Songs",
    "Samantha Songs",
    "Shruti Haasan Songs",
    "SS Rajamouli Songs"
]

# Dataset Path
DATASET_PATH = "features_raw.csv"
MODEL_PATH = "bci_model.joblib"
SCALER_PATH = "scaler.joblib"

# Startup automation
AUTO_PLAY_FIRST_SONG = True
JIOSAAVN_OPEN_WAIT_SECONDS = 8

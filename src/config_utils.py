import os
import json
from pathlib import Path

# Window Configuration
WINDOW_WIDTH = 485
WINDOW_HEIGHT = 220
WINDOW_TITLE = "Youtube Downloader 1.8"
WINDOW_ICON = Path(__file__).parent.parent / "assets" / "icon.ico"
FONT_FAMILY = "Roboto"

# Positions
error_message_pos = {"relx": 0.0, "rely": 1.03, "anchor": "sw"}
url_input_pos = {"relx": 0.0, "rely": 0.0, "anchor": "nw"}
validate_btn_pos = {"relx": 0.835, "rely": 0.0, "anchor": "n"}
download_btn_pos = {"relx": 0.835, "rely": 0.367, "anchor": "n"}
video_options_pos = {"relx": 0.0, "rely": 0.367, "anchor": "nw"}
file_loc_btn_pos = {"relx": 0.0, "rely": 0.18, "anchor": "nw"}

CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"
DOWNLOAD_FOLDER = ""

CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def save_config():
    save_folder()

def load_config():
    load_folder()

def save_folder():
    global DOWNLOAD_FOLDER
    with open(CONFIG_FILE, 'w') as file:
        json.dump({"download_folder": DOWNLOAD_FOLDER}, file)

def load_folder():
    global DOWNLOAD_FOLDER
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            DOWNLOAD_FOLDER = config.get("download_folder", str(Path.home()))
    else:
        DOWNLOAD_FOLDER = str(Path.home() / "Downloads")

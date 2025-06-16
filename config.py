import json
from user_default_folders import *

# WINDOW VARIABLE
WINDOW_TITLE = "Web Downloader 1.3"
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 160 #
WINDOW_ICON = "icon.ico"
APP_ELEMENTS_HEIGHT = 40

# PROGRAM FONTS
INTER_REGULAR = "fonts\Inter_Regular.ttf"
INTER_BLACK = "fonts\Inter_Black.ttf"

# CONFIG FILE FOLDER
DEFAULT_DOWNLOAD_LOCAL = USER_DOWNLOAD_FOLDER / "Web Downloader"
DEFAULT_APP_LOCAL = USER_DOCUMENTS_FOLDER / "Web Downloader"
CONFIG_FILE = DEFAULT_APP_LOCAL / "config.json"

def truncate_text(text: str, max_length: int):
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

class ConfigManager:
    def __init__(self):
        self.app_folder = DEFAULT_APP_LOCAL
        self.download_folder = str(DEFAULT_DOWNLOAD_LOCAL)
        
    def load_config(self):
        self.app_folder.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as file:
                    config = json.load(file)
                    self.download_folder = config.get("save_folder", self.download_folder)
            except json.JSONDecodeError as e:
                print(f"Erro ao ler o JSON de configuração: {e}")
            except Exception as e:
                print(f"Erro ao abrir arquivo JSON de configuração: {e}")
                
    def save_config(self, folder):
        if not self.app_folder.exists():
            self.app_folder.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as file:
            json.dump({"save_folder": folder}, file)

config_manager = ConfigManager()
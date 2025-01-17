import json
from pathlib import Path

# WINDOW VARIABLE
WINDOW_TITLE = "Youtube Downloader 1.2"
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 130
WINDOW_ICON = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
APP_FONT = "Roboto"

# POSITIONS
STATUS_LABEL_POS = {"x": 215, "y": 80, "anchor": "n"} # mensagem de erro etc...
URL_ENTRY_POS = {"x": 150, "y": 0, "anchor": "n"}
SELECT_FOLDER_POS = {"x": 150, "y": 40, "anchor": "n"}
VIDEO_RES_POS = {"x": 370, "y": 0, "anchor": "n"}
DOWNLOAD_BTN_POS = {"x": 370, "y": 40, "anchor": "n"}
DOWNLOAD_PROGRESS_POS = {"x": 215, "y": 80, "anchor": "n"}

# CONFIG FILE FOLDER
USER_DOCUMENTS = Path.home() / "Documents"
APP_FOLDER = USER_DOCUMENTS / "Youtube Downloader"
CONFIG_FILE =  APP_FOLDER / "config.json"
DOWNLOAD_FOLDER = ""

# TEXT COLORS
NORMAL_COLOR = "white"
ERROR_COLOR = "red"
SUCESS_COLOR = "green"
WAITING_COLOR = "orange"

class ConfigManager:
    def __init__(self):
        self.app_folder = APP_FOLDER
        self.download_folder = str(Path.home() / "Downloads")
        
    def load_confg(self):
        self.app_folder.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as file:
                    config = json.load(file)
                    self.download_folder = config.get("save_folder", self.download_folder)
            except json.JSONDecodeError as e:
                print(f"Erro ao ler o JSON de configuração: {e}")
            except:
                print(f"Erro ao abrir arquivo JSON de configuração: {e}")
    def save_config(self, folder):
        if not self.app_folder.exists():
            self.app_folder.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as file:
            json.dump({"save_folder": folder}, file)

config_manager = ConfigManager()
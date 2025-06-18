import json
from user_default_folders import *
import sys # Adicione esta linha
import os  # Adicione esta linha

# WINDOW VARIABLE
WINDOW_TITLE = "Web Downloader 1.3"
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 160 #
# MODIFICAR AQUI:
# Verifica se o aplicativo está rodando como um executável empacotado pelo PyInstaller
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Se sim, o caminho base é o diretório temporário do PyInstaller
    BUNDLE_DIR = sys._MEIPASS
else:
    # Caso contrário, estamos rodando a partir do script Python normal
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))

# Constrói o caminho completo para o ícone
WINDOW_ICON = os.path.join(BUNDLE_DIR, "icon.ico")

APP_ELEMENTS_HEIGHT = 40

# PROGRAM FONTS
# MODIFICAR AQUI PARA AS FONTES TAMBÉM
INTER_REGULAR = os.path.join(BUNDLE_DIR, "fonts", "Inter_Regular.ttf")
INTER_BLACK = os.path.join(BUNDLE_DIR, "fonts", "Inter_Black.ttf")


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
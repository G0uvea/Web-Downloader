import json
import sys
import os
import winreg
import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

class GetWindowsDefaultFolders():
    def __init__(self):
        pass

    @staticmethod
    def get_real_windows_folder(folder_name: str):
        guids = {
            "Downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
            "Documents": "Personal",
        }

        guid = guids.get(folder_name)

        if not guid:
            return Path.home() / folder_name

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")

            path_str, _ = winreg.QueryValueEx(key, guid)
            winreg.CloseKey(key)

            if path_str.startswith('%USERPROFILE%'):
                path_str = path_str.replace('%USERPROFILE%', str(Path.home()))

            return Path(path_str)
        except Exception as e:
            print(f"Erro ao obter pasta '{folder_name}' do Registro ({e}). Usando fallback padrão")
            return Path.home() / folder_name

# CONFIG FILE FOLDER
DEFAULT_DOWNLOAD_LOCAL = GetWindowsDefaultFolders.get_real_windows_folder("Downloads") / "Web Downloader"
DEFAULT_APP_LOCAL = GetWindowsDefaultFolders.get_real_windows_folder("Documents") / "Web Downloader"
CONFIG_FILE = DEFAULT_APP_LOCAL / "config.json"

if getattr(sys, 'frozen', False):
    ROOT_PATH = Path(sys._MEIPASS)
else:
    ROOT_PATH = Path(__file__).resolve().parent.parent

# Caminho para a pasta 'dependencies' na raiz do projeto
DEPENDENCIES_PATH = ROOT_PATH / "dependencies"

# Caminho para a subpasta 'ffmpeg' dentro de 'dependencies'
FFMPEG_BIN_PATH = DEPENDENCIES_PATH / "ffmpeg"

# Converter para string, pois os módulos podem esperar isso
DEPENDENCIES_PATH = str(DEPENDENCIES_PATH)
FFMPEG_BIN_PATH = str(FFMPEG_BIN_PATH)

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

class UIActions:
    def __init__(self):
        pass

    @staticmethod
    def CenterWindowToDisplay(Screen: ctk.CTk, width: int, height: int, scale_factor: float = 1.0):
        screen_width = Screen.winfo_screenwidth()
        screen_height = Screen.winfo_screenheight()
        x = int(((screen_width / 2) - (width / 2)) * scale_factor)
        y = int(((screen_height / 2) - (height / 1.5)) * scale_factor)
        return f"{width}x{height}+{x}+{y}"

    @staticmethod
    def truncate_text(text: str, max_length: int):
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        return text

    def select_folder_action(self, select_folder_btn: ctk.CTkButton):
        selected_folder = filedialog.askdirectory(initialdir=config_manager.download_folder)

        if selected_folder:
            config_manager.download_folder = selected_folder
            config_manager.save_config(selected_folder)
            select_folder_btn.configure(text=self.truncate_text(os.path.basename(selected_folder), 30))
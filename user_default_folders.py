import winreg
from pathlib import Path

def get_real_windows_folder(folder_name: str):
        guids = {
            "Downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
            "Documents": "Personal",
        }

        guid = guids.get(folder_name)

        if not guid:
            return Path.home() / folder_name

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")

            path_str, _ = winreg.QueryValueEx(key, guid)
            winreg.CloseKey(key)

            if path_str.startswith('%USERPROFILE%'):
                 path_str = path_str.replace('%USERPROFILE%', str(Path.home()))

            return Path(path_str)
        except Exception as e:
            print(f"Erro ao obter pasta '{folder_name}' do Registro ({e}). Usando fallback padrão")
            return Path.home() / folder_name


USER_DOWNLOAD_FOLDER = get_real_windows_folder("Downloads")
USER_DOCUMENTS_FOLDER = get_real_windows_folder("Documents")
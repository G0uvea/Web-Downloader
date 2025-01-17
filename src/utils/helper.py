import time
from tkinter import filedialog
from src.core.app_core import *

def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text


def select_folder_action(select_folder_btn):
    selected_folder = filedialog.askdirectory(initialdir=config_manager.download_folder)
    if selected_folder:
        config_manager.download_folder = selected_folder
        select_folder_btn.configure(text=truncate_text(config_manager.download_folder, 35))
        config_manager.save_config(selected_folder)

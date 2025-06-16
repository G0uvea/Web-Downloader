import customtkinter as ctk

from pathlib import Path
from src.main_interface import App
from config import *

def CenterWindowToDisplay(Screen: ctk.CTk, width: int, height: int, scale_factor: float = 1.0):
    screen_width = Screen.winfo_screenwidth()
    screen_height = Screen.winfo_screenheight()
    x = int(((screen_width/2) - (width/2)) * scale_factor)
    y = int(((screen_height/2) - (height/1.5)) * scale_factor)
    return f"{width}x{height}+{x}+{y}"

if __name__ == "__main__":
    window = ctk.CTk()
    window.title(WINDOW_TITLE)
    window.iconbitmap(WINDOW_ICON)
    window.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.geometry(CenterWindowToDisplay(window, WINDOW_WIDTH, WINDOW_HEIGHT, window._get_window_scaling()))
    window.resizable(False, False)
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = App(window)

    window.mainloop()

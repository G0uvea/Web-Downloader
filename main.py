import customtkinter as ctk
from gui.app_ui import AppUI

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
app_ui = AppUI(window)

window.mainloop()
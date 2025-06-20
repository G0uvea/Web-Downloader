import customtkinter as ctk
from gui.app_ui import AppUI # Importa a classe AppUI
from config.ui_settings import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE # Se for usar direto aqui


# Configurações iniciais do CustomTkinter
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

# Cria a janela principal do CustomTkinter
window = ctk.CTk()
# Não precisamos setar título, geometria e ícone aqui, pois AppUI fará isso.
# No entanto, se você quiser definir o título e a geometria antes de passar para AppUI, pode fazer aqui.
# Ex:
# window.title(WINDOW_TITLE)
# window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}") # A centralização será feita em AppUI

# Instancia a interface do usuário, passando a janela principal
app_ui = AppUI(window)

# Inicia o loop principal da interface
window.mainloop()
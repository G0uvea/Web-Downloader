import customtkinter as ctk
import queue
import os
import sys  # Importar sys para usar sys._MEIPASS

from config.ui_settings import *  # Importa os caminhos relativos do ui_settings.py
from config.settings import config_manager, UIActions
from downloader.core import AppCore  # Assumindo que core.py existe e é importado aqui


# --- FUNÇÃO PARA TRATAR CAMINHOS DE RECURSOS (PARA PYINSTALLER) ---
# Esta função deve estar em um local acessível onde os caminhos são usados.
# Colocá-la aqui em app_ui.py, antes de qualquer uso, é eficaz.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Em modo de desenvolvimento, usa o diretório atual do script.
        # Já que main.py está na raiz e app_ui.py em gui/, 
        # e os assets estão em gui/assets, os caminhos relativos funcionam.
        # O os.path.abspath(".") de onde o main.py é executado já é a raiz.
        base_path = os.path.abspath(".")

        # Junta o caminho base (sys._MEIPASS ou dir. atual) com o caminho relativo do recurso
    return os.path.join(base_path, relative_path)


# ------------------------------------------------------------------

class AppUI:
    def __init__(self, master):
        self.master = master

        config_manager.load_config()
        self.ui_actions = UIActions()

        # --- APLICAR resource_path AO ÍCONE DA JANELA ---
        self.master.title(WINDOW_TITLE)

        # CORREÇÃO PARA O ERRO 'winfo_rxbase': Removido o argumento `self.master.winfo_rxbase()`
        # A função CenterWindowToDisplay já tem um valor padrão para scale_factor (1.0).
        self.master.geometry(self.ui_actions.CenterWindowToDisplay(
            self.master, WINDOW_WIDTH, WINDOW_HEIGHT
        ))

        # AQUI ESTÁ A MUDANÇA CRÍTICA PARA O ÍCONE DA JANELA
        self.master.iconbitmap(resource_path(WINDOW_ICON))

        # INTERFACE FRAME
        self.frame = ctk.CTkFrame(self.master, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # GRID LAYOUT
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=0)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(3, weight=0)

        # URL INPUT
        self.url_entry = ctk.CTkEntry(
            self.frame,
            height=APP_ELEMENTS_HEIGHT,
            placeholder_text="Insira sua url aqui!",
            # APLICA resource_path PARA A FONTE
            font=ctk.CTkFont(family=resource_path(OUTFIT_BOLD), size=18),
            corner_radius=0,
            border_width=0,
            fg_color="#343638"
        )
        self.url_entry.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        # SELECT FOLDER BUTTON
        self.select_save_local_btn = ctk.CTkButton(
            self.frame,
            height=APP_ELEMENTS_HEIGHT,
            text=self.ui_actions.truncate_text(os.path.basename(config_manager.download_folder), 30),
            fg_color="#343638",
            hover_color="#034FC2",
            # APLICA resource_path PARA A FONTE
            font=ctk.CTkFont(family=resource_path(OUTFIT_BOLD), size=18),
            corner_radius=0,
            border_width=0,
            command=lambda: self.ui_actions.select_folder_action(self.select_save_local_btn)
        )
        self.select_save_local_btn.grid(row=1, column=0, sticky="nsew", padx=(0, 0), pady=0)

        # COMBOBOX DE RESOLUÇÕES
        self.select_resolution_cbb = ctk.CTkComboBox(
            self.frame,
            height=APP_ELEMENTS_HEIGHT,
            fg_color="#343638",
            text_color="white",
            # APLICA resource_path PARA A FONTE
            font=ctk.CTkFont(family=resource_path(OUTFIT_BOLD), size=18),
            corner_radius=0,
            border_width=0,
            values=[]
        )
        self.select_resolution_cbb.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=0)
        self.select_resolution_cbb.set("Resolução")
        self.select_resolution_cbb.configure(state="disabled")

        # DOWNLOAD BUTTON
        self.download_file_btn = ctk.CTkButton(
            self.frame,
            height=APP_ELEMENTS_HEIGHT,
            text="Baixar",
            fg_color="#343638",
            hover_color="#034FC2",
            # APLICA resource_path PARA A FONTE
            font=ctk.CTkFont(family=resource_path(OUTFIT_BOLD), size=18),
            corner_radius=0,
            border_width=0,
            state="disabled"
        )
        self.download_file_btn.grid(row=1, column=2, sticky="nsew", padx=(10, 0), pady=0)

        # TERMINAL INTERNO DO PROGRAMA
        self.terminal_output = ctk.CTkTextbox(
            self.frame,
            fg_color="#1E1E1E",
            text_color="#FFFFFF",
            # APLICA resource_path PARA A FONTE
            font=ctk.CTkFont(family=resource_path(SPACEMONO_BOLD), size=15),
            wrap="word",
            activate_scrollbars=True
        )
        self.terminal_output.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        self.terminal_output.configure(state="disabled")

        self.version_label = ctk.CTkLabel(
            self.frame,
            height=APP_ELEMENTS_HEIGHT,
            # APLICA resource_path PARA A FONTE
            font=ctk.CTkFont(family=resource_path(FUNNELSANS_BOLD), size=18),
            text="Versão 1.4"
        )
        self.version_label.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(10, 0))

        # THREAD PROCESS VARIABLES
        self.process = None
        self.output_queue = queue.Queue()

        # Instancia AppCore passando os widgets necessários
        self.app_core = AppCore(
            master=self.master,
            url_input=self.url_entry,
            select_resolution_cbb=self.select_resolution_cbb,
            download_file_btn=self.download_file_btn,
            select_save_local_btn=self.select_save_local_btn,
            app_terminal=self.terminal_output
        )

        # Conecta os eventos aos métodos do AppCore
        self.url_entry.bind("<Return>", lambda event: self.app_core.verify_url_and_enable_download())
        self.download_file_btn.configure(command=self.app_core.start_download)
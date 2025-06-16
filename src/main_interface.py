import customtkinter as ctk
from config import *
from tkinter import filedialog
from src.core.app_core import AppCore # Importa o AppCore

config_manager.load_config()

class App:
    def __init__(self, master):
        self.master = master

        # frame principal
        self.frame = ctk.CTkFrame(self.master, fg_color="#242424")
        self.frame.pack(fill="both", padx=10, pady=10)

        # Largura dos elementos da primeira linha (URL Entry e Botão Buscar)
        entry_width = 350 # Largura definida por você
        button_search_width = (WINDOW_WIDTH - 20) - (entry_width + 10) # Largura total - (largura entry + espaçamento)

        # Campo de URL
        self.url_entry = ctk.CTkEntry(
            self.frame,
            width=entry_width,
            height=APP_ELEMENTS_HEIGHT,
            placeholder_text="Insira a URL aqui",
            font=ctk.CTkFont(family=INTER_REGULAR, size=18),
            corner_radius=0,
            border_width=0,
            fg_color="#343638"
        )
        self.url_entry.place(x=0, y=0) # Posiciona o campo de URL

        # Botão Buscar
        self.search_btn = ctk.CTkButton(
            self.frame,
            width=button_search_width,
            height=APP_ELEMENTS_HEIGHT,
            text="Buscar",
            fg_color="#034FC2",
            hover_color="#003F9E",
            font=ctk.CTkFont(family=INTER_REGULAR, size=18),
            corner_radius=0,
            border_width=0
        )
        self.search_btn.place(x=entry_width + 10, y=0) # Posiciona ao lado da url_entry com 10px de espaçamento
        
        def select_folder_action():
            selected_folder = filedialog.askdirectory(initialdir=config_manager.download_folder)
            if selected_folder:
                config_manager.download_folder = selected_folder
                self.select_save_local_btn.configure(text=truncate_text(config_manager.download_folder, 35))
                config_manager.save_config(selected_folder)

        # Botão para selecionar local de salvamento
        self.select_save_local_btn = ctk.CTkButton(
            self.frame,
            width=WINDOW_WIDTH - 20, # Ajustado para caber no frame
            height=APP_ELEMENTS_HEIGHT,
            text=truncate_text(config_manager.download_folder, 50),
            fg_color="#343638",
            hover_color="#034FC2",
            font=ctk.CTkFont(family=INTER_BLACK, size=20),
            corner_radius=0,
            border_width=0,
            command=select_folder_action
        )
        self.select_save_local_btn.place(x=0, y=APP_ELEMENTS_HEIGHT + 10) # Posiciona o botão de salvar local com 10px de y (y=50 + 10)

        # Definindo a largura para o botão de baixar e o combobox
        download_button_width = (WINDOW_WIDTH - 20 - 10) / 2 # Metade do espaço disponível menos o espaçamento entre eles
        combobox_width = download_button_width # Mesma largura do botão

        # Botão para baixar os vídeos
        self.download_video_btn = ctk.CTkButton(
            self.frame,
            width=download_button_width,
            height=APP_ELEMENTS_HEIGHT,
            text="Baixar",
            fg_color="#034FC2",
            hover_color="#003F9E",
            font=ctk.CTkFont(family=INTER_REGULAR, size=18),
            corner_radius=0,
            border_width=0,
            state="disabled" # Desabilitado por padrão
        )
        # Posiciona o botão de download na mesma linha que o ComboBox, com 10px de y em relação ao select_save_local_btn
        self.download_video_btn.place(x=0, y=APP_ELEMENTS_HEIGHT + 60)

        # ComboBox para selecionar opção de download
        self.select_option = ctk.CTkComboBox(
            self.frame,
            width=combobox_width,
            height=APP_ELEMENTS_HEIGHT,
            fg_color="#034FC2",
            text_color="white",
            font=ctk.CTkFont(family=INTER_REGULAR, size=18),
            corner_radius=0,
            border_width=0,
            values=["Melhor qualidade", "Apenas Áudio"]
        )
        self.select_option.set("Melhor qualidade")
        # Posiciona o ComboBox à direita do botão Baixar com 10px de espaçamento
        self.select_option.place(x=download_button_width + 10, y=APP_ELEMENTS_HEIGHT + 60) 
        self.select_option.configure(state="disabled")

        # Instancia AppCore passando os widgets necessários
        self.app_core = AppCore(
            master=self.master,
            url_input=self.url_entry,
            select_option=self.select_option,
            download_btn=self.download_video_btn,
            select_folder_btn=self.select_save_local_btn,
            search_btn=self.search_btn # Passa o novo botão de busca
        )

        # Conecta os eventos aos métodos do AppCore
        # Removido self.url_entry.bind("<Return>", self.app_core.app_core_start)
        self.download_video_btn.configure(command=self.app_core.start_download) # Novo método para download
        self.search_btn.configure(command=self.app_core.verify_url_and_enable_download) # Conecta o botão Buscar
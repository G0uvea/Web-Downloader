import customtkinter as ctk
from src.utils.helper import *
from src.core.youtube_core import *

config_manager.load_confg()

class App:
    def __init__(self, master):
        self.master = master

        # frame principal
        self.frame = ctk.CTkFrame(self.master, fg_color="#242424")
        self.frame.pack(fill="both", padx=10, pady=10)

        # campo da url
        self.url_entry = ctk.CTkEntry(
            self.frame,
            width=300,
            height=30,
            placeholder_text="Insira uma URL válida!",
            font=ctk.CTkFont(family=APP_FONT, size=18),
            corner_radius=0,
            border_width=0,
            fg_color="#343638"
        )

        # botão de seleção de pasta
        self.select_folder = ctk.CTkButton(
            self.frame,
            width=300,
            height=30,
            text=truncate_text(config_manager.download_folder, 35),
            font=ctk.CTkFont(family=APP_FONT, size=18),
            corner_radius=0,
            border_width=0,
            fg_color="#343638",
            hover_color="#2f3032",
            command=lambda: select_folder_action(self.select_folder)
        )
        
        # combobox de resoluções de vídeo
        self.video_res = ctk.CTkComboBox(
            self.frame,
            width=120,
            height=30,
            font=ctk.CTkFont(family=APP_FONT, size=14),
            corner_radius=0,
            border_width=0,
            values=[]
        )
        
        # botão de download
        self.download_btn = ctk.CTkButton(
            self.frame,
            width=120,
            height=30,
            text="Baixar",
            font=ctk.CTkFont(family=APP_FONT, size=18),
            corner_radius=0,
            border_width=0
        )
       
        # messagem de status
        self.status_label = ctk.CTkLabel(
            self.frame,
            width=215,
            height=30,
            text="Bem-vindo!",
            text_color=NORMAL_COLOR,
            font=ctk.CTkFont(family=APP_FONT, size=16),
            corner_radius=0
        )

        # messagem de tempo
        self.time_label = ctk.CTkLabel(
            self.frame,
            width=215,
            height=30,
            text="Bem-vindo!",
            text_color=NORMAL_COLOR,
            font=ctk.CTkFont(family=APP_FONT, size=16),
            corner_radius=0
        )


        self.ytCore = YoutubeCore(
            master=self.master,
            status_message=self.status_label,
            input_entry=self.url_entry,
            resolution_cbb=self.video_res,
            download_btn=self.download_btn,
            select_folder_btn=self.select_folder,
            time_label = self.time_label
        )
        
        self.download_btn.configure(state=ctk.DISABLED) 
        self.video_res.set("Resolução") 
        self.video_res.configure(state=ctk.DISABLED)

        self.download_btn.configure(command=self.ytCore.download_verify)
        self.url_entry.bind("<Return>", lambda event: self.ytCore.youtube_get_video())

        self.url_entry.place(**URL_ENTRY_POS)
        self.select_folder.place(**SELECT_FOLDER_POS) 
        self.video_res.place(**VIDEO_RES_POS)
        self.download_btn.place(**DOWNLOAD_BTN_POS)
        self.status_label.place(**STATUS_LABEL_POS)
        self.time_label.place(**TIME_LABEL_POS)

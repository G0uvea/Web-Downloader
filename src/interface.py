import customtkinter as ctk
from src.utils import *

config_manager.load_confg()

class App:
    def __init__(self, master):
        self.master = master

        # frame principal
        self.frame = ctk.CTkFrame(self.master, fg_color="#242424")
        self.frame.pack(fill="both", padx=10, pady=10)

        # campo da url
        self.url_entry = ctk_basics.ctkEntry(
            self.frame,
            300,
            30,
            "Insira uma URL válida!",
            18,
            0,
            border_width=0,
            fg_color="#343638"
        )

        # botão de seleção de pasta
        self.select_folder = ctk_basics.ctkButton(
            self.frame,
            300,
            30,
            truncate_text(config_manager.download_folder, 35),
            18,
            0,
            border_width=0,
            fg_color="#343638",
            hover_color="#2f3032",
            command=lambda: select_folder_action(self.select_folder)
        )
        
        # combobox de resoluções de vídeo
        self.video_res = ctk_basics.ctkCbb(
            self.frame,
            120,
            30,
            14,
            0,
            border_width=0,
            values=[]
        )
        
        # botão de download
        self.download_btn = ctk_basics.ctkButton(
            self.frame,
            120,
            30,
            "Baixar",
            18,
            0,
            border_width=0
        )
       
        # barra de progresso do download
        # self.download_progress = ctk_basics.ctkProgress(
        #     self.frame,
        #     430,
        #     30,
        #     0,
        #     border_width=0
        # )
       
        # messagem de status
        self.status_label = ctk_basics.ctkLabel(
            self.frame,
            430,
            30,
            "Bem-vindo!",
            NORMAL_COLOR,
            16,
            0
        )

        self.get_video = GetVideoByURL(
            master=self.master,
            download_btn=self.download_btn,
            input_entry=self.url_entry,
            video_res=self.video_res,
            status_message=self.status_label
        )
        
        self.download_action = DownloadFile(
            master=master,
            video_res=self.video_res,
            input_entry=self.url_entry,
            status_message=self.status_label
        )

        self.download_btn.configure(state=ctk.DISABLED) 
        self.video_res.set("Resolução") 
        self.video_res.configure(state=ctk.DISABLED)

        self.download_btn.configure(command=self.download_action.download)
        self.url_entry.bind("<Return>", lambda event: self.get_video.check_input_url())

        self.url_entry.place(**URL_ENTRY_POS)
        self.select_folder.place(**SELECT_FOLDER_POS) 
        self.video_res.place(**VIDEO_RES_POS)
        self.download_btn.place(**DOWNLOAD_BTN_POS)
        self.status_label.place(**STATUS_LABEL_POS)

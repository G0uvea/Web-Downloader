import customtkinter as ctk
import threading 
import re
import json
import time
from pathlib import Path
from tkinter import filedialog
from src.app_core import *
from src.youtube_core import *

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

class DownloadFile():
    def __init__(self, master, input_entry, video_res, status_message):
        self.master = master
        self.input_entry = input_entry
        self.video_res = video_res
        self.status_message = status_message
        self.loading_animation_active = False

    def starting_loading_message(self):
        def animate_message():
            if not self.loading_animation_active:
                self.status_message.configure(text="Conteúdo Baixado!", text_color=SUCESS_COLOR)
                return
            base_message = "Download iniciado! Aguarde"
            dots = [".", "..", "..."]
            current_dots = dots[int(time.time() * 1) % len(dots)]

            self.status_message.configure(text=base_message + current_dots, text_color=WAITING_COLOR)
            self.master.after(300, animate_message)
            
        animate_message()

    def progress_callback(self, d):
        if d["status"] == "finished":
            self.loading_animation_active = False

    def download(self):
        try:
            selected_option = self.video_res.get()
            url = self.input_entry.get()
            print(f"Opção selecionada: {selected_option}")
            print(f"URL: {url}")
            
            if selected_option.startswith("Vídeo:"):
                resolution = selected_option.split(":")[1].strip()[:-1]
                print("Resolução: {resolution}")
                self.loading_animation_active = True
                threading.Thread(target=yt_core.download_video, args=(url, resolution, config_manager.download_folder, self.progress_callback)).start()
                self.starting_loading_message()
            elif selected_option.startswith("Apenas áudio"):
                self.loading_animation_active = True
                threading.Thread(target=yt_core.download_audio, args=(url, config_manager.download_folder, self.progress_callback)).start()
                self.starting_loading_message()
        except Exception as ex:
            print(f"Erro durante o download: {ex}")

class ConfigManager:
    def __init__(self):
        self.download_folder = str(Path.home() / "Downloads")

    def load_confg(self):
        APP_FOLDER.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as file:
                    config = json.load(file)
                    self.download_folder = config.get("save_folder", self.download_folder)
            except json.JSONDecodeError as e:
                print(f"Erro ao ler o JSON de configuração: {e}")
            except:
                print(f"Erro ao abrir arquivo JSON de configuração: {e}")
    def save_config(self, folder):
        if not APP_FOLDER.exists():
            APP_FOLDER.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as file:
            json.dump({"save_folder": folder}, file)

class ctkBasics:
    def __init__(self, font_family="Roboto"):
        self.font_family = font_family

    def ctkEntry(self, frame, width, height, text, size, corner_radius, **kwargs):
        return ctk.CTkEntry(frame, width=width, height=height, placeholder_text=text, font=ctk.CTkFont(family=self.font_family, size=size), corner_radius=corner_radius, **kwargs)

    def ctkButton(self,frame, width, height, text, size, corner_radius, **kwargs):
        return ctk.CTkButton(frame, width=width, height=height, text=text, font=ctk.CTkFont(family=self.font_family, size=size), corner_radius=corner_radius, **kwargs)

    def ctkCbb(self,frame, width, height, size, corner_radius, **kwargs):
        return ctk.CTkComboBox(frame, width=width, height=height, font=ctk.CTkFont(family=self.font_family, size=size), corner_radius=corner_radius, **kwargs)

    def ctkLabel(self,frame, width, height, text, text_color, size, corner_radius, **kwargs):
        return ctk.CTkLabel(frame, width=width, height=height, text=text, text_color=text_color, font=ctk.CTkFont(family=self.font_family, size=size), corner_radius=corner_radius, **kwargs)

    def ctkProgress(self,frame, width, height, corner_radius, **kwargs):
        return ctk.CTkProgressBar(frame, width=width, height=height, corner_radius=corner_radius, **kwargs)

class GetVideoByURL:
    def __init__(self, master, download_btn, input_entry, video_res, status_message):
        self.master = master
        self.download_btn = download_btn
        self.input_entry = input_entry
        self.video_res = video_res
        self.status_message = status_message
        self.loading_animation_active = False
        
    def fetch_video_resolutions(self, url):
        try:
            options = yt_core.get_video_resolutions(url)
            video_resolution = options['video']
            all_options = ["Vídeo: " + res for res in video_resolution] + ["Apenas áudio"]
            self.master.after(0, self.update_video_options, all_options)
            self.loading_animation_active = False
        except Exception as ex:
            self.loading_animation_active = False
            self.status_message.configure(text=f"ERRO! {ex}", text_color=ERROR_COLOR)

    def update_video_options(self, all_options):
        self.video_res.configure(values=all_options)
        if all_options:
            self.video_res.configure(state="readonly")
            self.video_res.set(all_options[0])
            self.download_btn.configure(state=ctk.NORMAL)

    def starting_loading_message(self):
        def animate_message():
            if not self.loading_animation_active:
                self.status_message.configure(text="Download liberado!", text_color=SUCESS_COLOR)
                return
            
            base_message = "Verificando! Aguarde"
            dots = [".", "..", "..."]
            current_dots = dots[int(time.time() * 1) % len(dots)]

            self.status_message.configure(text=base_message + current_dots, text_color=WAITING_COLOR)
            self.master.after(300, animate_message)
        
        animate_message()

    def check_input_url(self):
        url = self.input_entry.get()

        if not url:
            self.status_message.configure(text="URL INVÁLIDA!", text_color=ERROR_COLOR)
            return

        youtube_regex = re.compile(
            r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$'
        )

        if not youtube_regex.match(url):
            self.status_message.configure(text="URL INVÁLIDA!", text_color=ERROR_COLOR)
            return

        self.loading_animation_active = True
        threading.Thread(target=self.fetch_video_resolutions, args=(url,)).start()
        self.starting_loading_message()

config_manager = ConfigManager()
ctk_basics = ctkBasics()

import os
import shutil
import threading
import subprocess
import re
import yt_dlp as ytdl
import customtkinter as ctk
from src.core.app_core import config_manager 
from src.utils.helper import *
import time


class YoutubeCore:
    def __init__(self, master, status_message, input_entry, resolution_cbb, download_btn, select_folder_btn, time_label):
        self.resolution_filter = ["144p", "240p", "320p", "480p", "720p", "1080p"]
        self.video_resolution_format = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}
        self.master = master
        self.status_message = status_message
        self.input_entry = input_entry
        self.resolution_cbb = resolution_cbb
        self.download_btn = download_btn
        self.select_folder_btn = select_folder_btn
        self.time_label = time_label
       
        self.youtube_regex = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie|yout)\.(com|be)/.+$')
        self.end_download = False

        self.temp_folder = os.path.join(config_manager.app_folder, ".download_temp")
        os.makedirs(self.temp_folder, exist_ok=True)

    def get_resolutions(self, url):
        try:
            with ytdl.YoutubeDL(self.video_resolution_format) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                resolutions = {f"{fmt['height']}p" for fmt in formats if fmt.get('height') and f"{fmt['height']}p" in self.resolution_filter}
                self.video_duration = info.get('duration', 0)
                return {'video': sorted(resolutions, reverse=True)}
        except Exception as ex:
            self.status_message.configure(text=f"Erro ao buscar resoluções", text_color=ERROR_COLOR)
            return {'video': []}

    def download_verify(self):
        self.master.after(0, lambda: self.resolution_cbb.configure(state="disabled"))
        self.master.after(0, lambda: self.download_btn.configure(state="disabled"))
        self.master.after(0, lambda: self.input_entry.configure(state="disabled"))
        self.master.after(0, lambda: self.select_folder_btn.configure(state="disabled"))
        
        self.status_message.configure(text="Obtendo informações da url", text_color=WAITING_COLOR)

        try:
            selected_option = self.resolution_cbb.get()
            url = self.input_entry.get()

            if not url:
                self.status_message.configure(text="URL indisponível!", text_color=ERROR_COLOR)
                return

            if selected_option.startswith("Vídeo:"):
                resolution = selected_option.split(":")[1].strip()
                threading.Thread(target=self.download_and_convert, args=("video", url, resolution)).start()
            elif selected_option.startswith("Apenas áudio"):
                threading.Thread(target=self.download_and_convert, args=("audio", url, None)).start()
        except Exception as ex:
            self.status_message.configure(text=f"Erro no download", text_color=ERROR_COLOR)

    def download_and_convert(self, type, url, resolution):
        try:
            if resolution:
                resolution = resolution.replace("p", "")

            ydl_opts = {
                'outtmpl': os.path.join(self.temp_folder, '%(title)s.%(ext)s'),
                'noplaylist': True
            }

            if type == "video":
                ydl_opts['format'] = f'bestvideo[height={resolution}][ext=mp4]+bestaudio[ext=m4a]/best[height={resolution}][ext=mp4]/best'
            elif type == "audio":
                ydl_opts['format'] = 'bestaudio[ext=m4a]/best'

            with ytdl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                title = re.sub(r'[<>:"/\\|?*]', '_', info.get("title", "video"))
                filename_converted = f"{title}_converted.mp4" if type == "video" else f"{title}.aac"
                final_filename = f"{title}.mp4" if type == "video" else f"{title}.aac"
                converted_file = os.path.join(self.temp_folder, filename_converted)
 
                # Verifica se o arquivo baixado existe
                if not os.path.exists(downloaded_file):
                    raise FileNotFoundError(f"Arquivo baixado não encontrado: {downloaded_file}")
                
                start_time = time.time()

                if type == "video":
                    process = subprocess.Popen(
                        ['ffmpeg', '-i', downloaded_file, '-vcodec', 'libx264', '-acodec', 'aac', converted_file],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                    )
                elif type == "audio":
                    process = subprocess.Popen(
                        ['ffmpeg', '-i', downloaded_file, '-acodec', 'aac', '-b:a', '192k', converted_file],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                    )

                self.end_download = False
                threading.Thread(target=self.check_progress, args=(process, start_time)).start()
                process.wait()

                # Verifica se o arquivo convertido existe
                if not os.path.exists(converted_file):
                    raise FileNotFoundError(f"Arquivo convertido não encontrado: {converted_file}")
                
                final_path = os.path.join(config_manager.download_folder, final_filename)
                shutil.move(converted_file, final_path)
                os.remove(downloaded_file)
                
                self.status_message_shown = False
                self.end_download = True
                self.master.after(0, lambda: self.status_message.configure(
                    text="Download finalizado!", text_color=SUCESS_COLOR))
                
            self.master.after(0, lambda: self.resolution_cbb.configure(state="readonly"))
            self.master.after(0, lambda: self.download_btn.configure(state="normal"))
            self.master.after(0, lambda: self.input_entry.configure(state="normal"))
            self.master.after(0, lambda: self.select_folder_btn.configure(state="normal"))
        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            print(error_details)  # Para debug
            self.master.after(0, lambda: self.status_message.configure(
                text=f"Erro na conversão!", text_color=ERROR_COLOR))

    def check_progress(self, process, start_time):
        while True:
            # Leia a saída em tempo real do FFmpeg
            output = process.stderr.readline()
            
            # Se o processo terminou, saia do loop
            if output == '' and process.poll() is not None:
                break

            # Se a saída contém "time=", atualize o status
            if output and "time=" in output:
                self.update_status(output, start_time)

            # Pequeno delay para evitar consumo excessivo de CPU
            time.sleep(0.1)

    def update_status(self, line, start_time):
        time_part = re.search(r'time=\d{2}:\d{2}:\d{2}', line)
        if not time_part:
            return

        time_part = time_part.group(0).split('=')[1]
        elapsed_time = time.time() - start_time

        hours, minutes, seconds = map(float, time_part.split(":"))
        processed_time = int(hours * 3600 + minutes * 60 + seconds)

        # Evitar divisão por zero
        if processed_time > 0:
            remaining_time = max(0, (self.video_duration - processed_time) * (elapsed_time / processed_time))
            remaining_minutes, remaining_seconds = divmod(remaining_time, 60)
            remaining_hours, remaining_minutes = divmod(remaining_minutes, 60)

            self.master.after(0, lambda: self.time_label.configure(
                text=f"Tempo restante: {int(remaining_hours):02d}:{int(remaining_minutes):02d}:{int(remaining_seconds):02d}", text_color=REMAINING_TIME_COLOR))

            # Exibir "Download iniciado!" uma única vez
            if not hasattr(self, 'status_message_shown') or not self.status_message_shown:
                self.status_message_shown = True
                if self.end_download == False:
                    self.master.after(1000, lambda: self.status_message.configure(
                        text="Download iniciado!", text_color=WAITING_COLOR))
        else:
            # Caso ainda não haja progresso suficiente para calcular
            self.master.after(0, lambda: self.time_label.configure(
                text="Calculando tempo restante...", text_color=WAITING_COLOR))



    def youtube_get_video(self):
        self.master.after(0, lambda: self.resolution_cbb.configure(state="disabled"))
        self.master.after(0, lambda: self.download_btn.configure(state="disabled"))
        self.master.after(0, lambda: self.input_entry.configure(state="disabled"))
        self.master.after(0, lambda: self.select_folder_btn.configure(state="disabled"))    
        
        url = self.input_entry.get()
        if not url or not self.youtube_regex.match(url):
            self.status_message.configure(text="URL inválida!", text_color=ERROR_COLOR)
            return
        self.status_message.configure(text="Buscando resoluções", text_color=WAITING_COLOR)
        threading.Thread(target=self.fetch_resolutions, args=(url,)).start()

    def fetch_resolutions(self, url):
        try:
            video_resolutions = self.get_resolutions(url).get('video', [])
            all_options = ["Vídeo: " + res for res in video_resolutions] + ["Apenas áudio"]
            self.master.after(0, self.update_resolutions, all_options)
        except Exception as ex:
            self.status_message.configure(text=f"Erro ao buscar resoluções!", text_color=ERROR_COLOR)

    def update_resolutions(self, all_options):
        self.res_options = all_options
        self.resolution_cbb.configure(values=all_options)
        self.resolution_cbb.configure(state="readonly")
        self.download_btn.configure(state="normal")
        self.input_entry.configure(state="normal")
        self.select_folder_btn.configure(state="normal")
        self.status_message.configure(text="Download liberado!", text_color=SUCESS_COLOR)

        if all_options:
            self.resolution_cbb.set(all_options[0])
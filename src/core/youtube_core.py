import os
import shutil
import threading
import ffmpeg
import re
import yt_dlp as ytdl
import customtkinter as ctk
from src.core.app_core import config_manager 
from src.utils.helper import *


class YoutubeCore:
    def __init__(self, master, status_message, input_entry, resolution_cbb, download_btn):
        self.resolution_filter = ["144p", "240p", "320p", "480p", "720p", "1080p"]
        self.video_resolution_format = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}
        self.master = master
        self.status_message = status_message
        self.input_entry = input_entry
        self.resolution_cbb = resolution_cbb
        self.download_btn = download_btn
        self.youtube_regex = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')

        self.temp_folder = os.path.join(config_manager.app_folder, ".download_temp")
        os.makedirs(self.temp_folder, exist_ok=True)

    def get_resolutions(self, url):
        try:
            with ytdl.YoutubeDL(self.video_resolution_format) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                resolutions = {f"{fmt['height']}p" for fmt in formats if fmt.get('height') and f"{fmt['height']}p" in self.resolution_filter}
                return {'video': sorted(resolutions, reverse=True)}
        except Exception as ex:
            self.status_message.configure(text=f"Erro ao buscar resoluções: {ex}", text_color=ERROR_COLOR)
            return {'video': []}

    def download_verify(self):
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
            self.status_message.configure(text=f"Erro no download: {ex}", text_color=ERROR_COLOR)

    def download_and_convert(self, type, url, resolution):
        try:
            ydl_opts = {
                'format': f'bestvideo[height={resolution}]+bestaudio/best[height={resolution}]' if type == 'video' else 'bestaudio',
                'outtmpl': os.path.join(self.temp_folder, '%(title)s.%(ext)s'),
                'noplaylist': True
            }
            with ytdl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                filename, _ = os.path.splitext(downloaded_file)

                if type == "video":
                    converted_file = f"{filename}.mp4"
                    ffmpeg.input(downloaded_file).output(
                        converted_file, vcodec="libx264", acodec="aac", strict="experimental"
                    ).run(overwrite_output=True)
                elif type == "audio":
                    converted_file = f"{filename}.aac"
                    ffmpeg.input(downloaded_file).output(
                        converted_file, acodec="aac", audio_bitrate="192k"
                    ).run(overwrite_output=True)

                final_path = os.path.join(config_manager.download_folder, os.path.basename(converted_file))
                shutil.move(converted_file, final_path)
                os.remove(downloaded_file)

                self.status_message.configure(text="Download concluído!", text_color=SUCESS_COLOR)
        except Exception as ex:
            self.status_message.configure(text=f"Erro na conversão: {ex}", text_color=ERROR_COLOR)

    def youtube_get_video(self):
        url = self.input_entry.get()
        if not url or not self.youtube_regex.match(url):
            self.status_message.configure(text="URL inválida!", text_color=ERROR_COLOR)
            return
        self.status_message.configure(text="Buscando resoluções...", text_color=WAITING_COLOR)
        threading.Thread(target=self.fetch_resolutions, args=(url,)).start()

    def fetch_resolutions(self, url):
        try:
            video_resolutions = self.get_resolutions(url).get('video', [])
            all_options = ["Vídeo: " + res for res in video_resolutions] + ["Apenas áudio"]
            self.master.after(0, self.update_resolutions, all_options)
        except Exception as ex:
            self.status_message.configure(text=f"Erro ao buscar resoluções: {ex}", text_color=ERROR_COLOR)

    def update_resolutions(self, all_options):
        self.resolution_cbb.configure(values=all_options)
        if all_options:
            self.resolution_cbb.configure(state="readonly")
            self.resolution_cbb.set(all_options[0])
            self.download_btn.configure(state=ctk.NORMAL)
            self.status_message.configure(text="Download liberado!", text_color=SUCESS_COLOR)

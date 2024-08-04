import time
import tkinter as tk
import customtkinter as ctk
import os

from pytube import *
from tkinter import messagebox
from pathlib import Path
from moviepy.editor import *

# ----- Cores ----- #
frame_bg_col = "#242424"
url_text_col = "#A1A1A1"
status_error_col = "#fc2d31"
status_normal_col = "#ffffff"
progress_col = "#9003fc"
btn_hover_col = "#6700b5"
btn_fg_col = "#9003fc"

# ----- Label Texts ----- #
url_text_placeholder = "Insira a URL"
downloaded_file = "Arquivo Baixado com sucesso!"
progress_label_text = "0%"
download_video_btn = "Baixar Vídeo"
download_audio_btn = "Baixar Áudio"
select_download_path_btn = "Local de download"
video_resolutions = ["720p", "480p", "360p", "240p", "144p"]
video_res_label = "Qualidade do Vídeo:"

# ----- Font Configuration ----- #
font_family = "Roboto"
font_high_size = 20
font_normal_size = 18
font_small_size = 16
font_very_small_size = 12

# ----- Paths ----- #
download_folder = "D:\\Arquivos\\Downloads HDD\\Youtube Downloader"

# ----- Window Configuration ----- #
window = ctk.CTk()

window_width = 333
window_height = 220
window_title = "Youtube Downloader 1.7"

window.maxsize(window_width, window_height)
window.minsize(window_width, window_height)
window.title(window_title)
window.iconbitmap("icon.ico")

# ----- CTK Configuration ----- #
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ----- Start APP ----- #
try:
    video_clip_path = Path(download_folder).glob("*.mp4")

    for file in video_clip_path:
        os.remove(file)
except Exception as ex:
    print("Não foi possivel localizar um arquivo de vídeo no diretório.")
    print(f"{ex}")

#region DOWNLOADS METHODS
def video_download():
    url = url_input.get()
    resolution = video_resolution.get()

    try:
        yt = YouTube(url, on_progress_callback=download_progressing)
        stream = yt.streams.filter(res=resolution).first()

        progress_bar.place(x=156, y=140, anchor=tk.CENTER)
        progress_label.place(x=156, y=140, anchor=tk.CENTER)

        stream.download(output_path=download_folder)

        time.sleep(3)
        status_label.configure(text=downloaded_file, text_color=status_normal_col)
        status_label.place(x=156, y=180, anchor=tk.CENTER)

    except Exception as ex:
        status_label.configure(text=f"Ocorreu um erro. \n {str(ex)}", text_color=status_error_col)
        status_label.place(x=156, y=180, anchor=tk.CENTER)

def download_audio():
    url = url_input.get()

    try:
        yt = YouTube(url, on_progress_callback=download_progressing)
        stream = yt.streams.filter().first()

        progress_bar.place(x=156, y=140, anchor=tk.CENTER)
        progress_label.place(x=156, y=140, anchor=tk.CENTER)

        audio_file = stream.download(output_path=download_folder)

        time.sleep(3)
        status_label.configure(text=downloaded_file, text_color=status_normal_col)
        status_label.place(x=156, y=180, anchor=tk.CENTER)

        try:
            time.sleep(1)
            video_clip = VideoFileClip(str(audio_file))
            video_clip.audio.write_audiofile(f"{str(audio_file)}.mp3")
        except Exception as ex:
            status_label.configure(text=f"Ocorreu um erro. \n Não foi possivel converter o arquivo de video em audio.", text_color=status_error_col)

    except Exception as ex:
        status_label.configure(text=f"Ocorreu um erro. \n {str(ex)}", text_color=status_error_col)
        status_label.place(x=156, y=180, anchor=tk.CENTER)

#endregion

#region DOWNLOAD PROGRESSING
def download_progressing(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completed = bytes_downloaded / total_size * 100
    progress_bar.set(float(percentage_completed / 100))

    progress_label.configure(text=f"{str(int(percentage_completed))}%")
    progress_label.update()
#endregion

#region FONTS
high_font_size = ctk.CTkFont(family=font_family, size=font_high_size)
normal_font_size = ctk.CTkFont(family=font_family, size=font_normal_size)
small_font_size = ctk.CTkFont(family=font_family, size=font_small_size)
very_small_font_size = ctk.CTkFont(family=font_family, size=font_very_small_size)
#endregion

#region FRAME
frame = ctk.CTkFrame(window, fg_color=frame_bg_col)
frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)
#endregion

#region URL INPUT
url_input = ctk.CTkEntry(frame, width=312, height=25, text_color=url_text_col, corner_radius=10, font=normal_font_size, placeholder_text=url_text_placeholder, placeholder_text_color=url_text_col)
url_input.place(x=156, y=20, anchor=tk.CENTER)
#endregion

#region PROGRESS BAR
progress_bar = ctk.CTkProgressBar(frame, width=312, height=25, progress_color=progress_col)
progress_label = ctk.CTkLabel(frame, text=progress_label_text, font=normal_font_size)
status_label = ctk.CTkLabel(frame, text=downloaded_file, font=small_font_size)

# progress_bar.place(x=156, y=140, anchor=tk.CENTER)
# progress_label.place(x=156, y=140, anchor=tk.CENTER)
# status_label.place(x=156, y=180, anchor=tk.CENTER)


progress_bar.set(float(0))
progress_label.configure(text="0%")

#endregion

#region VIDEO RESOLUTIONS
video_resolution_label = ctk.CTkLabel(frame, text=video_res_label, font=small_font_size)
video_resolution_label.place(x=71, y=60, anchor=tk.CENTER)

video_resolution = ctk.StringVar()
video_resolutions_cbb = ctk.CTkComboBox(frame, width=140, height=25, values=video_resolutions, font=normal_font_size, variable=video_resolution)
video_resolutions_cbb.set("720p")
video_resolutions_cbb.place(x=241, y=60, anchor=tk.CENTER)
#endregion

#region DOWNLOAD VIDEO BUTTON
video_download_btn = ctk.CTkButton(frame, text=download_video_btn, width=140, height=25, hover=btn_hover_col, fg_color=btn_fg_col, corner_radius=10, font=normal_font_size, command=video_download)
video_download_btn.pack(pady=5)
video_download_btn.place(x=71, y=100, anchor=tk.CENTER)
#endregion

#region DOWNLOAD AUDIO BUTTON
audio_download_btn = ctk.CTkButton(frame, text=download_audio_btn, width=140, height=25, hover=btn_hover_col, fg_color=btn_fg_col, corner_radius=10, font=normal_font_size, command=download_audio)
audio_download_btn.pack(pady=5)
audio_download_btn.place(x=241, y=100, anchor=tk.CENTER)
#endregion

window.mainloop()
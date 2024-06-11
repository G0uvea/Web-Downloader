import time
import tkinter as tk
import customtkinter as ctk
import os

from pytube import *
from manager import *
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from pathlib import Path
from moviepy.editor import *

window = ctk.CTk()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

window.maxsize(window_width, window_height)
window.minsize(window_width, window_height)
window.title(window_title)

video_download_folder = os.path.expanduser("~" + "\\downloads\\YoutubeDownloader\\Videos")
audio_download_folder = os.path.expanduser("~" + "\\downloads\\YoutubeDownloader\\Audios")

#region DOWNLOADS METHODS
def video_download():
    url = url_input.get()
    resolution = video_resolution.get()

    progress_bar.place(x=156, y=140, anchor=tk.CENTER)
    progress_label.place(x=156, y=140, anchor=tk.CENTER)
    status_label.place(x=156, y=180, anchor=tk.CENTER)

    try:
        yt = YouTube(url, on_progress_callback=download_progressing)
        stream = yt.streams.filter(res=resolution).first()

        stream.download(output_path=video_download_folder)
    except Exception as ex:
        # status_label.configure(text=f"Erro {str(ex)}", text_color=error_color)
        progress_bar.set(float(0))
        progress_label.configure(text="0%")
        messagebox.showerror("Erro!", f"{str(ex)}")

def download_audio():
    url = url_input.get()

    progress_bar.place(x=156, y=140, anchor=tk.CENTER)
    progress_label.place(x=156, y=140, anchor=tk.CENTER)
    status_label.place(x=156, y=180, anchor=tk.CENTER)

    try:
        yt = YouTube(url, on_progress_callback=download_progressing)
        stream = yt.streams.filter().first()
        audio_file = stream.download(output_path=audio_download_folder)

        time.sleep(1)
        path_list = Path(audio_download_folder).glob("*.mp4")

        video_clip = VideoFileClip(str(audio_file))
        video_clip.audio.write_audiofile(f"{str(audio_file)}.mp3")

        time.sleep(1)
        os.remove(audio_file)

    except Exception as ex:
        # status_label.configure(text=f"Erro {str(ex)}", text_color=error_color)
        progress_bar.set(float(0))
        progress_label.configure(text="0%")
        messagebox.showerror("Erro!", f"{str(ex)}")

#endregion

#region DOWNLOAD PROGRESSING
def download_progressing(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completed = bytes_downloaded / total_size * 100

    progress_label.configure(text=f"{str(int(percentage_completed))}%")
    progress_label.update()

    progress_bar.set(float(percentage_completed / 100))
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

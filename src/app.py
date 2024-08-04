import time
import tkinter as tk
import customtkinter as ctk

from manager import *
<<<<<<< HEAD
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from pathlib import Path
from moviepy.editor import *
=======
>>>>>>> parent of c65d886 (Release 1.3 - Correção de Bugs)

from video_download import *
from audio_download import *

class Main(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

<<<<<<< HEAD
video_download_folder = os.path.expanduser("~" + "\\downloads\\YoutubeDownloader\\Videos")
audio_download_folder = os.path.expanduser("~" + "\\downloads\\YoutubeDownloader\\Audios")
=======
        self.maxsize(WIDTH, HEIGHT)
        self.minsize(WIDTH, HEIGHT)
        self.title(TITLE)
        
        #region FONTS
        program_font = ctk.CTkFont(family=font_family, size=20)
        small_font = ctk.CTkFont(family=font_family, size=16)
        very_small_font = ctk.CTkFont(family=font_family, size=12)
        #endregion
>>>>>>> parent of c65d886 (Release 1.3 - Correção de Bugs)

        #region FRAME
        frame = ctk.CTkFrame(self, fg_color=frame_bg_color)
        frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)
        #endregion

        #region URL INPUT
        url_input = ctk.CTkEntry(frame, width=312, height=25, text_color=label_text_color, corner_radius=10, font=program_font, placeholder_text=input_label_text, placeholder_text_color=label_text_color)
        url_input.place(x=156, y=20, anchor=tk.CENTER)
        #endregion

        #region VIDEO RESOLUTIONS
        video_resolution_label = ctk.CTkLabel(frame, text=select_video_resoluction_label, font=small_font)
        video_resolution_label.place(x=80, y=60, anchor=tk.CENTER)

<<<<<<< HEAD
        stream.download(output_path=video_download_folder)
    except Exception as ex:
        # status_label.configure(text=f"Erro {str(ex)}", text_color=error_color)
        progress_bar.set(float(0))
        progress_label.configure(text="0%")
        messagebox.showerror("Erro!", f"{str(ex)}")
=======
        video_resolution = ctk.StringVar()
        video_resolutions_cbb = ctk.CTkComboBox(frame, width=140, height=25, values=video_resolutions, font=program_font, variable=video_resolution)
        video_resolutions_cbb.set("720p")
        video_resolutions_cbb.place(x=240, y=60, anchor=tk.CENTER)
        #endregion
>>>>>>> parent of c65d886 (Release 1.3 - Correção de Bugs)


        #region AUDIO RESOLUTIONS
        audio_resolution_label = ctk.CTkLabel(frame, text=select_audio_resoluction_label, font=small_font)
        audio_resolution_label.place(x=80, y=100, anchor=tk.CENTER)

<<<<<<< HEAD
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
=======
        audio_resolution = ctk.StringVar()
        audio_resolutions_cbb = ctk.CTkComboBox(frame, width=140, height=25, values=audio_resolutions, font=program_font, variable=audio_resolution)
        audio_resolutions_cbb.set("128khz")
        audio_resolutions_cbb.place(x=240, y=100, anchor=tk.CENTER)
        #endregion

        #region DOWNLOAD VIDEO BUTTON
        video_download_btn = ctk.CTkButton(frame, text=video_download_btn_lbl, width=140, height=25, hover=btn_hover_color, fg_color=btn_fg_color, corner_radius=10, font=program_font, command=download_video)
        video_download_btn.pack(pady=5)
        video_download_btn.place(x=80, y=140, anchor=tk.CENTER)
        #endregion
>>>>>>> parent of c65d886 (Release 1.3 - Correção de Bugs)

        #region DOWNLOAD AUDIO BUTTON
        audio_download_btn = ctk.CTkButton(frame, text=audio_download_btn_lbl, width=140, height=25, hover=btn_hover_color, fg_color=btn_fg_color, corner_radius=10, font=program_font, command=download_audio)
        audio_download_btn.pack(pady=5)
        audio_download_btn.place(x=240, y=140, anchor=tk.CENTER)
        #endregion

        # progress_bar = ctk.CTkProgressBar(frame, width=420, height=25, progress_color=progress_color)
        # progress_label = ctk.CTkLabel(frame, text=progress_label_text, font=program_font)
        # status_label = ctk.CTkLabel(frame, text=status_label_text, font=very_small_font)

main = Main()
main.mainloop()

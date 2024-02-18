import tkinter as tk
import customtkinter as ctk
from pytube import YouTube

WIDTH = 640
HEIGHT = 160

class Main(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.geometry("640x160")
        self.maxsize(WIDTH, HEIGHT)
        self.minsize(WIDTH, HEIGHT)
        self.title("Youtube Downloader 1.0.0")
        
        def download_video():
            url = input_entry.get()
            resolution = resolution_str.get()

            progress_bar.place(x=260, y=80, anchor=tk.CENTER)
            progress_label.place(x=20, y=80, anchor=tk.CENTER)
            status_label.place(x=WIDTH / 2.1, y=120, anchor=tk.CENTER)

            try:
                yt = YouTube(url, on_progress_callback=download_progressing)
                stream = yt.streams.filter(res=resolution).first()

                stream.download()
            except Exception as e:
                error_color = "#fc2d31"
                status_label.configure(text=f"Erro {str(e)}", text_color=error_color)

        def download_progressing(stream, chunk, bytes_remaining):
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage_completed = bytes_downloaded / total_size * 100

            progress_label.configure(text=f"{str(int(percentage_completed))}%")
            progress_label.update()

            progress_bar.set(float(percentage_completed / 100))

        font_family = "Fira Code"
        program_font = ctk.CTkFont(family=font_family, size=20)
        small_font = ctk.CTkFont(family=font_family, size=16)
        very_small_font = ctk.CTkFont(family=font_family, size=12)

        frame_bg_color = "#242424"
        frame = ctk.CTkFrame(self, fg_color=frame_bg_color)
        frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

        input_label_text = "Coloque uma URL do youtube"
        label_text_color = "#A1A1A1"
        input_entry = ctk.CTkEntry(frame, width=460, height=25, text_color=label_text_color, corner_radius=10, font=program_font, placeholder_text=input_label_text, placeholder_text_color=label_text_color)
        input_entry.place(x=235, y=30, anchor=tk.CENTER)

        button_hover_color = "#6700b5"
        button_fg_color = "#9003fc"
        button_text = "Download"
        download_button = ctk.CTkButton(frame, text=button_text, width=140, height=25, hover_color=button_hover_color, fg_color=button_fg_color,corner_radius=10, font=program_font, command=download_video)
        download_button.pack(pady=5)
        download_button.place(x=545, y=80, anchor=tk.CENTER)

        resolutions = ["720p", "360p", "240p", "144p"]
        resolution_str = ctk.StringVar()
        resolution_cbb = ctk.CTkComboBox(frame, width=140, height=25, values=resolutions, font=program_font, variable=resolution_str)
        resolution_cbb.set("720p")
        resolution_cbb.place(x=545, y=30, anchor=tk.CENTER)

        progress_color = "#9003fc"
        progress_bar = ctk.CTkProgressBar(frame, width=420, height=25, progress_color=progress_color)

        progress_label_text = "100%"
        progress_label = ctk.CTkLabel(frame, text=progress_label_text, font=program_font)

        status_label_text = "Download feito com sucesso"
        status_label = ctk.CTkLabel(frame, text=status_label_text, font=very_small_font)


main = Main()
main.mainloop()

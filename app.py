import re
import customtkinter as ctk
import threading
from tkinter import filedialog
from src import config_utils
from src import ctk_utils
from src import youtube_module
from src import app_logic

config_utils.load_config()
DOWNLOAD_FOLDER = config_utils.DOWNLOAD_FOLDER

def select_local_file_download():
    global DOWNLOAD_FOLDER
    selected_folder = filedialog.askdirectory(initialdir=DOWNLOAD_FOLDER)
    if selected_folder:
        DOWNLOAD_FOLDER = selected_folder
        config_utils.save_config()
        save_local_file.configure(text=app_logic.truncate_text(DOWNLOAD_FOLDER, 35))

def fetch_video_resolutions(url):
    options = youtube_module.get_video_resolutions(url)
    video_resolution = options['video']
    audio_qualities = options['audio']
    all_options = ['Vídeo: ' + res for res in video_resolution] + ['Áudio: ' + audio for audio in audio_qualities]

    window.after(0, update_video_options, all_options)

def update_video_options(all_options):
    videos_options.configure(values=all_options)
    if all_options:
        videos_options.set(all_options[0])
    videos_options.place(**config_utils.video_options_pos)
    download_button.place(**config_utils.download_btn_pos)

def more_actions():
    url = url_input.get()
    
    if not url:
        error_message.place(**config_utils.error_message_pos)
        return

    youtube_regex = re.compile(
        r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')
    
    if not youtube_regex.match(url):
        error_message.place(**config_utils.error_message_pos)
        return

    threading.Thread(target=fetch_video_resolutions, args=(url,)).start()

def download():
    selected_option = videos_options.get()
    url = url_input.get()
    if selected_option.startswith("Vídeo:"):
        resolution = selected_option.split(": ")[1]
        threading.Thread(target=youtube_module.download_video, args=(url, resolution, DOWNLOAD_FOLDER)).start()
    if selected_option.startswith("Áudio:"):
        audio_quality = selected_option.split(": ")[1]
        threading.Thread(target=youtube_module.download_audio, args=(url, audio_quality, DOWNLOAD_FOLDER)).start()

if __name__ == "__main__":
    window = ctk.CTk()
    window.title(config_utils.WINDOW_TITLE)
    window.iconbitmap(config_utils.WINDOW_ICON)
    window.maxsize(config_utils.WINDOW_WIDTH, config_utils.WINDOW_HEIGHT)
    window.minsize(config_utils.WINDOW_WIDTH, config_utils.WINDOW_HEIGHT)
    window.geometry(ctk_utils.CenterWindowToDisplay(window, config_utils.WINDOW_WIDTH, config_utils.WINDOW_HEIGHT, window._get_window_scaling()))
    window.resizable(False, False)

    config_utils.load_config()

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    frame = ctk.CTkFrame(window, fg_color="#242424")
    frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)
    
    url_input = ctk_utils.create_entry(
        frame, 
        300, 
        25, 
        18, 
        "#A1A1A1", 
        5, 
        "Insira a URL!")
    url_input.place(**config_utils.url_input_pos)

    validate_button = ctk_utils.create_button(
        frame, 
        150, 
        25, 
        "Buscar", 
        18, 
        corner_radius=5, 
        command=more_actions)
    validate_button.place(**config_utils.validate_btn_pos)

    save_local_file = ctk_utils.create_button(
        frame, 
        463, 
        25, 
        app_logic.truncate_text(DOWNLOAD_FOLDER, 35), 
        18, 
        command=select_local_file_download, 
        fg_color="#343638", 
        border_width=2, 
        border_color="#565b5e", 
        corner_radius=5,
        hover=False)
    save_local_file.place(**config_utils.file_loc_btn_pos)

    videos_options = ctk_utils.create_cbb(
        frame, 
        300, 
        25, 
        18, 
        [], 
        None,
        state="readonly")
    videos_options.place_forget()
    # videos_options.place(**config_utils.video_options_pos)

    download_button = ctk_utils.create_button(
        frame, 
        150, 
        25, 
        "Baixar", 
        18, 
        corner_radius=5, 
        command=download)
    download_button.place_forget()
    # download_button.place(**config_utils.download_btn_pos)

    error_message = ctk_utils.create_label(
        frame, 
        "URL INDISPONÍVEL", 
        "#fc2d31", 
        16)
    error_message.place_forget()
    # error_message.place(**config_utils.error_message_pos)

    window.mainloop()

import re
import customtkinter as ctk
import threading
from tkinter import filedialog
from src import config_utils
from src import ctk_utils
from src import youtube_module
from src import app_logic

config_utils.load_config()

def select_local_file_download():
    selected_folder = filedialog.askdirectory(initialdir=config_utils.DOWNLOAD_FOLDER)
    if selected_folder:
        config_utils.DOWNLOAD_FOLDER = selected_folder
        config_utils.save_config()
        save_local_file.configure(text=app_logic.truncate_text(config_utils.DOWNLOAD_FOLDER, 35))

def fetch_video_resolutions(url):
    options = youtube_module.get_video_resolutions(url)
    video_resolution = options['video']
    all_options = ['Vídeo: ' + res for res in video_resolution] + ['Apenas áudio']

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
        url_unavaliable.place(**config_utils.error_message_pos)
        return

    youtube_regex = re.compile(
        r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')
    
    if not youtube_regex.match(url):
        url_unavaliable.place(**config_utils.error_message_pos)
        return

    threading.Thread(target=fetch_video_resolutions, args=(url,)).start()

def progress_callback(d):
    if d['status'] == 'downloading':
        percent_str = re.sub(r'[^\d.]+', '', d['_percent_str'])
        percent = float(percent_str)
        window.after(0, download_progress.set, percent / 100)

def download():
    download_progress.place(**config_utils.download_progress_pos)
    selected_option = videos_options.get()
    url = url_input.get()
    if selected_option.startswith("Vídeo:"):
        resolution = selected_option.split(": ")[1]
        threading.Thread(target=youtube_module.download_video, args=(url, resolution, config_utils.DOWNLOAD_FOLDER, progress_callback)).start()
    if selected_option.startswith("Apenas áudio"):
        threading.Thread(target=youtube_module.download_audio, args=(url, config_utils.DOWNLOAD_FOLDER, progress_callback)).start()

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
        29, 
        18, 
        "#A1A1A1", 
        0, 
        "Insira a URL!",
        border_width=0)
    url_input.place(**config_utils.url_input_pos)

    validate_button = ctk_utils.create_button(
        frame, 
        150, 
        25, 
        "Buscar", 
        18,
        fg_color="#8036cf", 
        hover_color="#572390",
        corner_radius=0,
        border_width=0,
        command=more_actions)
    validate_button.place(**config_utils.validate_btn_pos)

    save_local_file = ctk_utils.create_button(
        frame, 
        466, 
        25, 
        app_logic.truncate_text(config_utils.DOWNLOAD_FOLDER, 35), 
        18, 
        command=select_local_file_download, 
        fg_color="#343638", 
        border_width=0, 
        hover_color="#2c2e30", 
        corner_radius=0)
    save_local_file.place(**config_utils.file_loc_btn_pos)

    videos_options = ctk_utils.create_cbb(
        frame, 
        300, 
        29, 
        18, 
        [], 
        None,
        corner_radius=0,
        border_width=0,
        state="readonly")
    videos_options.place_forget()
    # videos_options.place(**config_utils.video_options_pos)

    download_button = ctk_utils.create_button(
        frame, 
        150, 
        25, 
        "Baixar", 
        18, 
        fg_color="#8036cf", 
        corner_radius=0,
        hover_color="#572390",
        command=download)
    download_button.place_forget()
    # download_button.place(**config_utils.download_btn_pos)

    download_progress = ctk_utils.create_progress_bar(
        frame, 
        466,
        25,
        corner_radius=0,
        fg_color="#343638",
        border_width=0, 
        progress_color="#8036cf")
    download_progress.set(0)
    download_progress.place_forget()
    # download_progress.place(**config_utils.download_progress_pos)

    url_unavaliable = ctk_utils.create_label(
        frame, 
        "URL INDISPONÍVEL", 
        "#fc2d31", 
        16)
    # url_unavaliable.place_forget()
    url_unavaliable.place(**config_utils.error_message_pos)

    window.mainloop()

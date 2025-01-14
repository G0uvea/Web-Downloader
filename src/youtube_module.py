import yt_dlp as ytdl
from src import config_utils

VIDEO_RESOLUTIONS = ["144p", "240p", "320p", "480p", "720p", "1080p"]

def get_video_resolutions(url):
    ytdl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    }
    
    with ytdl.YoutubeDL(ytdl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])

        resolutions = set()
        audio_qualities = set()
        for fmt in formats:
            if fmt.get('height'):
                res = (f"{fmt['height']}p")
                if res in VIDEO_RESOLUTIONS:
                    resolutions.add(res)
            elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                bitrate = fmt.get('abr')
                if bitrate:
                    rounded_bitrate = round(bitrate)
                    if 128 <= rounded_bitrate <= 320:
                        audio_qualities.add(f"{rounded_bitrate} kbps")

        return {
            'video': sorted(list(resolutions), reverse=True),
            'audio': sorted(list(audio_qualities), reverse=True)
        }

def download_video(url, resolution, download_folder):
    ytdl_opts = {
        'format': f'bestvideo[height={resolution}]+bestaudio/best', 
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s', 
        'merge_output_format': 'mp4'
    }

    with ytdl.YoutubeDL(ytdl_opts) as ydl:
        ydl.download([url])

def download_audio(url, audio_quality, download_folder):
    ytdl_opts = { 
        'format': f'bestaudio[abr={audio_quality}]', 
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s', 
        'postprocessors': [{ 
            'key': 'FFmpegExtractAudio', 
            'preferredcodec': 'mp3', 
            'preferredquality': '192' }]
    }

    with ytdl.YoutubeDL(ytdl_opts) as ydl:
        ydl.download([url])
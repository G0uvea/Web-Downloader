import yt_dlp as ytdl

class YtCore:
    video_resolutions = ["144p", "240p", "320p", "480p", "720p", "1080p"]

    def get_video_resolutions(self, url):
        ytdl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        }

        with ytdl.YoutubeDL(ytdl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])

            resolutions = set()
            for fmt in formats:
                if fmt.get('height'):
                    res = (f"{fmt['height']}p")
                    if res in self.video_resolutions:
                        resolutions.add(res)

            return {
                'video': sorted(list(resolutions), reverse=True)
            }
        
    def download_video(self, url, resolution, download_folder, progress_callback):
        ytdl_opts = {
            'format': f'bestvideo[height={resolution}]+bestaudio/best', 
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s', 
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_callback]
        }

        with ytdl.YoutubeDL(ytdl_opts) as ydl:
            ydl.download([url])

    def download_audio(self, url, download_folder, progress_callback):
        ytdl_opts = { 
            'format': f'bestaudio',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s', 
            'postprocessors': [{ 
                'key': 'FFmpegExtractAudio', 
                'preferredcodec': 'mp3', 
                'preferredquality': '192' 
            }],
            'progress_hooks': [progress_callback]
        }

        with ytdl.YoutubeDL(ytdl_opts) as ydl:
            ydl.download([url])

yt_core = YtCore()

import os
import shutil
import threading
import subprocess
import re
import yt_dlp as ytdl
import customtkinter as ctk
import time

# Importa as configurações, incluindo BUNDLE_DIR
from config import * 

class AppCore:
    def __init__(self, master, url_input: ctk.CTkEntry, select_option: ctk.CTkComboBox, download_btn: ctk.CTkButton, select_folder_btn: ctk.CTkButton, search_btn: ctk.CTkButton):
        self.master = master
        self.url_input = url_input
        self.select_option = select_option
        self.download_btn = download_btn
        self.select_folder_btn = select_folder_btn
        self.search_btn = search_btn

        self.video_url = ""
        self.end_download = False
        self.video_duration = 0
        self.video_info = None # Armazenar informações do vídeo/playlist aqui
        self.is_playlist = False # Flag para indicar se a URL é de uma playlist
        self.playlist_title = None # Título da playlist, se aplicável

        # Define o diretório temporário para downloads intermediários
        self.temp_folder = os.path.join(config_manager.app_folder, ".download_temp")
        os.makedirs(self.temp_folder, exist_ok=True)

        # Tenta encontrar o caminho do FFmpeg na inicialização
        self.ffmpeg_path = self._find_ffmpeg_path()

        # Regex mais genérica para URLs de vídeo, yt-dlp fará a validação mais robusta
        self.video_url_regex = re.compile(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/\S*)?$')

    def _find_ffmpeg_path(self):
        """
        Tenta encontrar os executáveis ffmpeg.exe e ffprobe.exe na raiz
        do diretório da aplicação empacotada (BUNDLE_DIR).
        Ambos são necessários para o yt-dlp funcionar corretamente na maioria dos casos.
        """
        ffmpeg_exe_path = os.path.join(BUNDLE_DIR, "ffmpeg.exe")
        ffprobe_exe_path = os.path.join(BUNDLE_DIR, "ffprobe.exe")
        
        ffmpeg_found = os.path.exists(ffmpeg_exe_path)
        ffprobe_found = os.path.exists(ffprobe_exe_path)

        if ffmpeg_found and ffprobe_found:
            print(f"[INFO] FFmpeg e FFprobe encontrados em: {BUNDLE_DIR}")
            return BUNDLE_DIR # Retorna o diretório onde ambos estão
        else:
            if not ffmpeg_found:
                print(f"[AVISO] ffmpeg.exe não encontrado no caminho esperado: {ffmpeg_exe_path}.")
            if not ffprobe_found:
                print(f"[AVISO] ffprobe.exe não encontrado no caminho esperado: {ffprobe_exe_path}.")
            print("[AVISO] Para downloads de áudio ou fusão de vídeo/áudio, FFmpeg e FFprobe são essenciais.")
            print("[AVISO] Verifique se os arquivos ffmpeg.exe e ffprobe.exe estão na pasta 'dependencies' e se o .bat está configurado corretamente.")
            return None

    def verify_url_and_enable_download(self):
        """
        Verifica a validade da URL inserida, determina se é um vídeo ou playlist,
        e habilita/desabilita os botões de download.
        """
        self.video_url = self.url_input.get()
        if not self.video_url or not self.video_url_regex.match(self.video_url):
            print("[ERRO] Por favor, coloque uma URL válida no campo.")
            self._set_download_ui_state("disabled")
            return

        print("[INFO] Verificando URL...")
        # Desabilita todos os botões e campos, exceto o de buscar, durante a verificação
        self.master.after(0, lambda: self._set_ui_state("disabled", ignore_search=True))
        threading.Thread(target=self._fetch_info_and_enable_buttons).start()

    def _fetch_info_and_enable_buttons(self):
        """
        Busca informações da URL usando yt-dlp e define o estado da UI.
        Permite que o yt-dlp detecte playlists.
        """
        try:
            ydl_opts = {
                'quiet': True,
                'simulate': True, # Apenas simula, não baixa
                'force_generic_extractor': True, # Para tentar com extratores genéricos
                'timeout': 60,
                "retries": 5,
                'ignoreerrors': True # Adicionado para ignorar erros de vídeos indisponíveis na simulação
            }
            # Adiciona o caminho do FFmpeg se ele foi encontrado
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path

            with ytdl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.video_url, download=False)
                # Verifica se a URL retornou alguma informação. Mesmo com ignoreerrors=True,
                # se a URL principal (da playlist) for inválida ou a única mídia estiver indisponível,
                # info pode ser None ou um dicionário vazio/incompleto.
                if info is None or (info.get('_type') == 'playlist' and not info.get('entries')):
                    raise ValueError("Não foi possível obter informações válidas da URL.")
            
            self.video_info = info # Armazena as informações do vídeo/playlist

            # Verifica se é uma playlist
            if info.get('_type') == 'playlist':
                self.is_playlist = True
                self.playlist_title = info.get('title', 'Playlist Sem Título') # Adiciona um fallback
                print(f"[INFO] URL de playlist detectada: '{self.playlist_title}'")
                # Verifica se a playlist possui entradas válidas
                if not info.get('entries') or all(entry.get('extractor_key') == 'Generic' and entry.get('url') is None for entry in info.get('entries', [])):
                    print("[AVISO] A playlist pode não conter vídeos válidos ou acessíveis.")
            else:
                self.is_playlist = False
                self.playlist_title = None
                print("[INFO] URL de vídeo individual detectada.")
            
            print("[INFO] URL válida. Botão 'Baixar' habilitado.")
            self.master.after(0, lambda: self._set_download_ui_state("normal"))
            self.master.after(0, lambda: self.search_btn.configure(state="normal")) # Reabilita o botão Buscar

        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERRO] Falha na validação da URL: {ex} - Detalhes: {error_details}")
            print("[ERRO] Por favor, coloque uma URL válida no campo.")
            self.master.after(0, lambda: self._set_download_ui_state("disabled"))
            self.master.after(0, lambda: self._set_ui_state("normal")) # Reabilita todos os campos e botões em caso de erro

    def start_download(self, event=None):
        """
        Inicia o processo de download em uma thread separada.
        """
        self.video_url = self.url_input.get() # Pega a URL novamente para garantir

        if not self.video_info: # Garante que as informações do vídeo foram obtidas
            print("[ERRO] Nenhuma informação do vídeo/playlist disponível. Por favor, verifique a URL novamente.")
            self._set_ui_state("normal")
            return

        # Desabilita botões e campos durante o processamento
        self._set_ui_state("disabled")
        print("[INFO] Iniciando download...")
        
        threading.Thread(target=self._process_download).start()

    def _process_download(self):
        """
        Gerencia o tipo de download (vídeo/áudio) e chama a função de download e conversão.
        """
        try:
            selected_option = self.select_option.get()
            download_type = "video" if selected_option == "Melhor qualidade" else "audio"

            self._download_and_convert(download_type, self.video_url, self.video_info)

        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERRO] Erro no processamento: {error_details}")
            self._set_ui_state("normal")

    def _download_and_convert(self, download_type, url, info):
        """
        Executa o download do vídeo ou playlist, e faz a conversão se necessário.
        Gerencia o destino do arquivo (pasta normal ou pasta da playlist).
        """
        try:
            # Limpa o diretório temporário antes de cada download
            self._cleanup_temp_folder()

            ydl_opts = {
                'timeout': 60,
                "retries": 10,
                'progress_hooks': [self._download_progress_hook],
                'quiet': True,
                'ignoreerrors': True # Continua mesmo que um vídeo da playlist falhe
            }

            # Adiciona o caminho do FFmpeg se ele foi encontrado
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path

            final_ext = "" # Inicializa a extensão final

            if download_type == "video":
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                final_ext = "mp4"
            elif download_type == "audio":
                ydl_opts['format'] = 'bestaudio[ext=m4a]/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'aac',
                    'preferredquality': '192',
                }]
                final_ext = "m4a"

            # Define o diretório de destino e o outtmpl com base no tipo de URL (playlist ou vídeo individual)
            target_download_folder = config_manager.download_folder
            if self.is_playlist and self.playlist_title:
                # Sanitiza o título da playlist para o nome da pasta
                playlist_folder_name = re.sub(r'[<>:"/\\|?*]', '_', self.playlist_title)
                target_download_folder = os.path.join(config_manager.download_folder, playlist_folder_name)
                os.makedirs(target_download_folder, exist_ok=True)
                ydl_opts['outtmpl'] = os.path.join(target_download_folder, '%(title)s.%(ext)s')
                ydl_opts['noplaylist'] = False # Permite download de playlist
                print(f"[INFO] Baixando para a pasta da playlist: {target_download_folder}")
            else:
                ydl_opts['outtmpl'] = os.path.join(self.temp_folder, '%(title)s.%(ext)s')
                ydl_opts['noplaylist'] = True # Garante download de vídeo individual
                print("[INFO] Baixando vídeo individual.")

            with ytdl.YoutubeDL(ydl_opts) as ydl:
                # O download=True executa o download real
                download_info = ydl.extract_info(url, download=True)
                if download_info is None:
                    # Pode acontecer de download_info ser None se todos os vídeos de uma playlist
                    # com ignoreerrors=True forem indisponíveis, ou se for um vídeo único inválido.
                    raise ValueError("Falha ao extrair informações do vídeo/playlist durante o download.")
                
                if not self.is_playlist:
                    # Para vídeos individuais, move do temp_folder para o destino final
                    # Se download_info for uma lista (para playlists), precisamos lidar com isso
                    # Mas aqui é apenas para vídeos individuais, então esperamos um dict.
                    final_file_path_temp = download_info.get('_filepath')

                    if not final_file_path_temp or not os.path.exists(final_file_path_temp):
                        print("[AVISO] _filepath não encontrado ou arquivo não existe. Tentando encontrar o arquivo mais recente.")
                        recent_files = sorted(
                            [os.path.join(self.temp_folder, f) for f in os.listdir(self.temp_folder) 
                             if os.path.isfile(os.path.join(self.temp_folder, f))],
                            key=os.path.getmtime, reverse=True
                        )
                        if recent_files:
                            final_file_path_temp = recent_files[0]
                            print(f"[INFO] Arquivo mais recente encontrado: {final_file_path_temp}")
                        else:
                            raise FileNotFoundError(f"Arquivo final não encontrado no diretório temporário para '{info.get('title', 'video')}'.")

                    time.sleep(1) # Garante que o arquivo foi totalmente gravado

                    title = re.sub(r'[<>:"/\\|?*]', '_', info.get("title", "video"))
                    destination_path = os.path.join(config_manager.download_folder, f"{title}.{final_ext}")
                    
                    # Se o arquivo já existir na pasta de destino, adiciona um sufixo
                    counter = 1
                    original_destination_path = destination_path
                    while os.path.exists(destination_path):
                        name, ext = os.path.splitext(original_destination_path)
                        destination_path = f"{name} ({counter}){ext}"
                        counter += 1

                    shutil.move(final_file_path_temp, destination_path)
                
                self.end_download = True
                print("\n[SUCESSO] Download finalizado!")
                
        except ytdl.DownloadError as e:
            print(f"\n[ERRO] Erro de download: {e}")
            # Em playlists, este erro pode indicar que todos os vídeos falharam ou um erro crítico
            # Mas yt-dlp com 'ignoreerrors': True geralmente continua
        except FileNotFoundError as e:
            print(f"\n[ERRO] Erro de arquivo: {e}")
        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n[ERRO] Erro na conversão ou movimentação: {error_details}")
        finally:
            self._cleanup_temp_folder() # Limpa a pasta temporária
            self._set_ui_state("normal")
            print("[INFO] Pronto para baixar! Insira uma nova URL ou baixe o último vídeo.")

    def _download_progress_hook(self, d):
        """
        Hook para exibir o progresso do download.
        """
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)

            if total_bytes > 0:
                progress = (downloaded_bytes / total_bytes) * 100
                filename = d.get('filename', 'arquivo desconhecido')
                # Simplifica a exibição para evitar caminhos muito longos no console
                display_filename = os.path.basename(filename) 
                print(f"[PROGRESSO] Baixando '{display_filename}': {progress:.1f}%", end='\r')
            else:
                print(f"[PROGRESSO] Baixando...", end='\r')
        elif d['status'] == 'finished':
            print("\n[INFO] Download de item concluído, processando...")
        elif d['status'] == 'error':
            filename = d.get('filename', 'arquivo desconhecido')
            print(f"\n[AVISO] Erro ao baixar '{filename}': {d.get('error', 'Erro desconhecido')}")


    def _cleanup_temp_folder(self):
        """
        Limpa todos os arquivos e subpastas do diretório temporário.
        """
        if os.path.exists(self.temp_folder):
            for filename in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Falha ao deletar {file_path}. Razão: {e}')
        # Garante que a pasta temporária existe após a limpeza, caso tenha sido removida
        os.makedirs(self.temp_folder, exist_ok=True)


    def _set_ui_state(self, state, ignore_search=False):
        """
        Controla o estado de todos os elementos da UI.
        'ignore_search' é True quando o botão 'Buscar' está em ação.
        """
        self.master.after(0, lambda: self.url_input.configure(state=state))
        self.master.after(0, lambda: self.select_folder_btn.configure(state=state))
        
        if not ignore_search:
            self.master.after(0, lambda: self.search_btn.configure(state=state))
        else:
            self.master.after(0, lambda: self.search_btn.configure(state="normal"))

        if state == "disabled":
            self.master.after(0, lambda: self.download_btn.configure(state="disabled"))
            self.master.after(0, lambda: self.select_option.configure(state="disabled"))

    def _set_download_ui_state(self, state):
        """
        Controla especificamente o estado dos botões de download e select option.
        """
        self.master.after(0, lambda: self.download_btn.configure(state=state))
        self.master.after(0, lambda: self.select_option.configure(state="readonly" if state == "normal" else "disabled"))

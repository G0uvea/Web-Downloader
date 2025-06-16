import os
import shutil
import threading
import subprocess
import re
import yt_dlp as ytdl
import customtkinter as ctk
import time

from config import *

class AppCore:
    def __init__(self, master, url_input: ctk.CTkEntry, select_option: ctk.CTkComboBox, download_btn: ctk.CTkButton, select_folder_btn: ctk.CTkButton, search_btn: ctk.CTkButton):
        self.master = master
        self.url_input = url_input
        self.select_option = select_option
        self.download_btn = download_btn
        self.select_folder_btn = select_folder_btn
        self.search_btn = search_btn # Novo botão de busca

        self.video_url = ""
        self.end_download = False
        self.video_duration = 0
        self.video_info = None # Armazenar informações do vídeo aqui

        self.temp_folder = os.path.join(config_manager.app_folder, ".download_temp")
        os.makedirs(self.temp_folder, exist_ok=True)

        # Regex mais genérica para URLs de vídeo, yt-dlp fará a validação mais robusta
        self.video_url_regex = re.compile(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/\S*)?$')

    def verify_url_and_enable_download(self):
        self.video_url = self.url_input.get()
        if not self.video_url or not self.video_url_regex.match(self.video_url):
            print("[ERRO] Por favor, coloque uma URL válida no campo.")
            # Desabilitar botões de download e select option se a URL for inválida
            self._set_download_ui_state("disabled")
            return

        # Tentativa de buscar informações básicas para validar a URL com yt-dlp
        print("[INFO] Verificando URL...")
        self.master.after(0, lambda: self._set_ui_state("disabled", ignore_search=True)) # Desabilita tudo exceto o search_btn
        threading.Thread(target=self._fetch_info_and_enable_buttons).start()

    def _fetch_info_and_enable_buttons(self):
        try:
            ydl_opts = {
                'quiet': True,
                'simulate': True, # Não baixa, apenas simula e extrai info
                'force_generic_extractor': True, # Para tentar com extratores genéricos
                'noplaylist': True,
                'timeout': 60,
                "retries": 5
            }
            with ytdl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.video_url, download=False)
                if info is None:
                    raise ValueError("Não foi possível obter informações da URL.")
            
            self.video_info = info # Armazena as informações do vídeo
            print("[INFO] URL válida. Botão 'Baixar' habilitado.")
            self.master.after(0, lambda: self._set_download_ui_state("normal"))
            self.master.after(0, lambda: self.search_btn.configure(state="normal")) # Reabilitar o botão Buscar

        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERRO] Falha na validação da URL: {ex} - Detalhes: {error_details}")
            print("[ERRO] Por favor, coloque uma URL válida no campo.")
            self.master.after(0, lambda: self._set_download_ui_state("disabled"))
            self.master.after(0, lambda: self._set_ui_state("normal")) # Reabilitar todos os campos e botões em caso de erro

    def start_download(self, event=None):
        self.video_url = self.url_input.get() # Pega a URL novamente para garantir

        if not self.video_info: # Garante que as informações do vídeo foram obtidas
            print("[ERRO] Nenhuma informação do vídeo disponível. Por favor, verifique a URL novamente.")
            self._set_ui_state("normal")
            return

        # Desabilitar botões e campos durante o processamento
        self._set_ui_state("disabled")
        print("[INFO] Iniciando download...")
        
        threading.Thread(target=self._process_download).start()

    def _process_download(self):
        try:
            selected_option = self.select_option.get()
            
            download_type = "video" if selected_option == "Melhor qualidade" else "audio"

            self._download_and_convert(download_type, self.video_url, self.video_info) # Passa video_info

        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERRO] Erro no processamento: {error_details}")
            self._set_ui_state("normal")

    def _download_and_convert(self, download_type, url, info): # Recebe info
        try:
            # Limpa o diretório temporário antes de cada download
            self._cleanup_temp_folder()

            ydl_opts = {
                'outtmpl': os.path.join(self.temp_folder, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'timeout': 60,
                "retries": 10,
                'progress_hooks': [self._download_progress_hook],
                'quiet': True,
            }

            if download_type == "video":
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            elif download_type == "audio":
                ydl_opts['format'] = 'bestaudio[ext=m4a]/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'aac',
                    'preferredquality': '192',
                }]

            with ytdl.YoutubeDL(ydl_opts) as ydl:
                # O download=True agora realmente baixa o vídeo
                # As informações retornadas aqui podem ser mais completas após o download
                download_info = ydl.extract_info(url, download=True)
                if download_info is None:
                    raise ValueError("Falha ao extrair informações do vídeo durante o download.")
                
                # Usa o 'filepath' retornado pelo yt-dlp, que é mais confiável
                # para encontrar o arquivo final após o download e pós-processamento.
                # Ele pode vir de download_info ou info (do verify_url), dependendo do cenário
                # Priorizamos o download_info pois é o mais atualizado após o download.
                final_file_path_temp = download_info.get('_filepath') # Caminho completo do arquivo baixado

                if not final_file_path_temp or not os.path.exists(final_file_path_temp):
                    # Se _filepath não for suficiente, tentamos uma abordagem alternativa:
                    # Buscamos o arquivo que foi mais recentemente modificado no diretório temporário.
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


                # Garante que o arquivo foi totalmente gravado
                time.sleep(1) 

                # Usa o título original do vídeo para o nome do arquivo final
                title = re.sub(r'[<>:"/\\|?*]', '_', info.get("title", "video"))
                
                # Garante a extensão correta para o arquivo final
                if download_type == "video":
                    final_ext = "mp4"
                elif download_type == "audio":
                    final_ext = "m4a" # yt-dlp com FFmpegExtractAudio para aac pode resultar em m4a ou aac

                # O nome do arquivo real pode ter o ID do vídeo ou outros caracteres,
                # então renomeamos para o padrão desejado.
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
        except FileNotFoundError as e:
            print(f"\n[ERRO] Erro de arquivo: {e}")
        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n[ERRO] Erro na conversão ou movimentação: {error_details}")
        finally:
            self._cleanup_temp_folder() # Limpa a pasta temporária novamente
            self._set_ui_state("normal")
            print("[INFO] Pronto para baixar! Insira uma nova URL ou baixe o último vídeo.")

    def _download_progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)

            if total_bytes > 0:
                progress = (downloaded_bytes / total_bytes) * 100
                print(f"[PROGRESSO] Baixando: {progress:.1f}%", end='\r')
            else:
                print(f"[PROGRESSO] Baixando...", end='\r')
        elif d['status'] == 'finished':
            print("\n[INFO] Download concluído, processando...")

    def _cleanup_temp_folder(self):
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
        
        # O search_btn só é desabilitado se não for ignorado
        if not ignore_search:
            self.master.after(0, lambda: self.search_btn.configure(state=state))
        else: # Se ignorado, ele mantém o estado anterior (provavelmente "normal")
            self.master.after(0, lambda: self.search_btn.configure(state="normal"))

        # download_btn e select_option têm estado controlado por _set_download_ui_state
        # mas são desabilitados por _set_ui_state quando o download começa
        if state == "disabled":
            self.master.after(0, lambda: self.download_btn.configure(state="disabled"))
            self.master.after(0, lambda: self.select_option.configure(state="disabled"))
        # Quando reabilitando (state == "normal"), o estado do download_btn e select_option
        # é gerenciado por _set_download_ui_state.

    def _set_download_ui_state(self, state):
        """
        Controla especificamente o estado dos botões de download e select option.
        """
        self.master.after(0, lambda: self.download_btn.configure(state=state))
        self.master.after(0, lambda: self.select_option.configure(state="readonly" if state == "normal" else "disabled"))
import shutil
import threading
import re
import yt_dlp as ytdl
import customtkinter as ctk
import time
import os

from config.settings import config_manager, FFMPEG_BIN_PATH, UIActions, DEFAULT_APP_LOCAL

class AppCore:
    def __init__(self, master, url_input: ctk.CTkEntry, select_resolution_cbb: ctk.CTkComboBox,
                 download_file_btn: ctk.CTkButton, select_save_local_btn: ctk.CTkButton, app_terminal: ctk.CTkTextbox):
        self.master = master
        self.url_input = url_input
        self.select_resolution_cbb = select_resolution_cbb
        self.download_file_btn = download_file_btn
        self.select_save_local_btn = select_save_local_btn
        self.app_terminal = app_terminal
        self.ui_actions = UIActions()

        self.video_url = ""
        self.video_info = None
        self.is_playlist = False
        self.playlist_title = None
        self.available_formats = []

        # Configura a pasta temporária para downloads, usando DEFAULT_APP_LOCAL
        self.temp_folder = os.path.join(DEFAULT_APP_LOCAL, ".download_temp")
        os.makedirs(self.temp_folder, exist_ok=True)

        self._configure_terminal_tags()

        # Encontra o caminho do FFmpeg
        self.ffmpeg_path = self._find_ffmpeg_path()

        # Define o estado inicial da UI
        self._set_initial_ui_state()
        self._write_to_terminal("[INFO] Pronto para baixar! Insira uma URL.")

    def _configure_terminal_tags(self):
        """
        Configura as tags de cor para o terminal da aplicação.
        """
        self.app_terminal.tag_config("error_tag", foreground="#FF0000")    # Vermelho vibrante
        self.app_terminal.tag_config("warning_tag", foreground="#FFFF00")  # Amarelo vibrante
        self.app_terminal.tag_config("success_tag", foreground="#00FF00")  # Verde vibrante
        self.app_terminal.tag_config("info_tag", foreground="#87CEEB")     # Azul claro
        self.app_terminal.tag_config("progress_tag", foreground="#ADD8E6") # Azul acinzentado

    def _set_initial_ui_state(self):
        """
        Define o estado inicial dos elementos da interface do usuário.
        """
        self.download_file_btn.configure(state="disabled")
        self.select_resolution_cbb.configure(state="disabled")
        self.select_resolution_cbb.set("Selecione a Resolução")

    def _write_to_terminal(self, message):
        """
        Escreve uma mensagem no terminal da aplicação com uma tag de cor apropriada.
        """
        tag = "info_tag"
        if message.startswith("[ERRO]"):
            tag = "error_tag"
        elif message.startswith("[AVISO]"):
            tag = "warning_tag"
        elif message.startswith("[SUCESSO]"):
            tag = "success_tag"
        elif message.startswith("[PROGRESSO]"):
            tag = "progress_tag"

        # Garante que a atualização do terminal ocorra na thread principal da UI
        self.master.after(0, lambda: self._update_terminal_output(message, tag))

    def _update_terminal_output(self, message, tag):
        """
        Atualiza o widget do terminal, inserindo a mensagem e rolando para o final.
        """
        self.app_terminal.configure(state="normal")
        self.app_terminal.insert(ctk.END, message + "\n", tag)
        self.app_terminal.see(ctk.END)
        self.app_terminal.configure(state="disabled")

    def _find_ffmpeg_path(self):
        """
        Verifica se o FFmpeg e o FFprobe estão disponíveis no caminho configurado.
        """
        ffmpeg_exe_path = os.path.join(FFMPEG_BIN_PATH, "ffmpeg.exe")
        ffprobe_exe_path = os.path.join(FFMPEG_BIN_PATH, "ffprobe.exe")

        ffmpeg_found = os.path.exists(ffmpeg_exe_path)
        ffprobe_found = os.path.exists(ffprobe_exe_path)

        if ffmpeg_found and ffprobe_found:
            self._write_to_terminal(
                f"[INFO] FFmpeg e FFprobe encontrados em: {FFMPEG_BIN_PATH}")
            return FFMPEG_BIN_PATH
        else:
            if not ffmpeg_found:
                self._write_to_terminal(f"[AVISO] ffmpeg.exe não encontrado no caminho esperado: {ffmpeg_exe_path}.")
            if not ffprobe_found:
                self._write_to_terminal(f"[AVISO] ffprobe.exe não encontrado no caminho esperado: {ffprobe_exe_path}.")
            self._write_to_terminal(
                "[AVISO] Para downloads de áudio ou fusão de vídeo/áudio, FFmpeg e FFprobe são essenciais.")
            self._write_to_terminal(
                "[AVISO] Verifique se os arquivos ffmpeg.exe, ffprobe.exe e suas DLLs estão na pasta 'dependencies/ffmpeg'.")
            return None

    def verify_url_and_enable_download(self):
        """
        Verifica a URL inserida pelo usuário e habilita os botões de download
        após obter as informações do vídeo/playlist.
        """
        self.video_url = self.url_input.get().strip()
        if not self.video_url:
            self._write_to_terminal("[ERRO] Por favor, insira uma URL no campo.")
            self._set_download_ui_state("disabled")
            return

        self._write_to_terminal("[INFO] Verificando URL...")
        # Desabilita a UI durante a verificação para evitar interações indesejadas
        self.master.after(0, lambda: self._set_ui_state("disabled"))
        threading.Thread(target=self._fetch_info_and_enable_buttons).start()

    def _fetch_info_and_enable_buttons(self):
        """
        Busca informações do vídeo/playlist usando yt-dlp e popula a combobox.
        """
        try:
            ydl_opts = {
                'quiet': True,
                'simulate': True,
                'force_generic_extractor': True,
                'timeout': 60,
                "retries": 5,
                'ignoreerrors': True,
                'listformats': True
            }
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path
            else:
                self._write_to_terminal(
                    "[AVISO] FFmpeg não configurado. Certos formatos de vídeo ou áudio podem não estar disponíveis.")

            with ytdl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.video_url, download=False)

                if info is None:
                    raise ValueError(
                        "Não foi possível obter informações válidas da URL. Pode ser um erro ou URL inválida.")

            self.video_info = info
            self.available_formats = []

            if info.get('_type') == 'playlist':
                self.is_playlist = True
                self.playlist_title = info.get('title', 'Playlist Sem Título')
                self._write_to_terminal(f"[INFO] URL de playlist detectada: '{self.playlist_title}'")

                all_playlist_formats = []
                if info.get('entries'):
                    for entry in info['entries']:
                        if entry and entry.get('formats'):
                            all_playlist_formats.extend(entry['formats'])

                if all_playlist_formats:
                    self.available_formats = self._filter_formats(all_playlist_formats)
                else:
                    self._write_to_terminal(
                        "[AVISO] Nenhuma entrada válida ou formatos encontrados na playlist.")
                    # Se não houver formatos na playlist, self.available_formats ficará vazio,
                    # o que será tratado pela função _update_resolution_combobox.

            else:
                self.is_playlist = False
                self.playlist_title = None
                self._write_to_terminal("[INFO] URL de vídeo individual detectada.")
                self.available_formats = self._filter_formats(info.get('formats', []))

            self._update_resolution_combobox()
            self.master.after(0, lambda: self._set_download_ui_state("normal"))
            self._write_to_terminal("[INFO] URL válida. Selecione a resolução e clique em 'Baixar'.")

        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            self._write_to_terminal(f"[ERRO] Falha na validação da URL: {ex}")
            self._write_to_terminal("[ERRO] Por favor, insira uma URL válida no campo.")
            self.master.after(0, lambda: self._set_download_ui_state("disabled"))
        finally:
            # Reabilita a UI após a verificação (mesmo em caso de erro)
            self.master.after(0, lambda: self._set_ui_state("normal"))

    @staticmethod
    def _filter_formats(formats):
        """
        Filtra e organiza os formatos de vídeo e áudio disponíveis,
        retornando apenas as opções realmente extraídas pelo yt-dlp.
        Prioriza a maior resolução de vídeo ou a maior qualidade de áudio.
        """
        video_resolutions = set()
        audio_formats = set()

        desired_audio_abrs = [160, 192, 320]  # kbps (bitrates de áudio desejados)

        for f in formats:
            # Filtra formatos de vídeo MP4 com codec de vídeo e altura definida
            if f.get('vcodec') != 'none' and f.get('ext') == 'mp4' and f.get('height'):
                height = f.get('height')
                video_resolutions.add(f"Vídeo {height}p")

            # Filtra formatos de áudio-only com codec de áudio e sem codec de vídeo
            if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                abr = f.get('abr')
                if abr:
                    # Encontra o ABR desejado mais próximo para categorização
                    closest_abr = min(desired_audio_abrs, key=lambda x: abs(x - abr))
                    audio_formats.add(f"Áudio {closest_abr}kbps")

        # Ordena as resoluções de vídeo em ordem decrescente (do maior para o menor)
        sorted_video_resolutions = sorted(
            [res for res in list(video_resolutions) if re.search(r'(\d+)p', res)],
            key=lambda x: int(re.search(r'(\d+)p', x).group(1)),
            reverse=True
        )

        # Ordena os formatos de áudio em ordem decrescente de bitrate
        sorted_audio_formats = sorted(
            list(audio_formats),
            key=lambda x: int(re.search(r'(\d+)kbps', x).group(1)) if re.search(r'(\d+)kbps', x) else 0,
            reverse=True
        )

        options = []
        options.extend(sorted_video_resolutions) # Adiciona vídeos primeiro
        options.extend(sorted_audio_formats)     # Depois adiciona áudios

        # Retorna apenas as opções realmente encontradas.
        # Se a lista estiver vazia, a combobox será configurada para "Nenhuma opção disponível".
        return options

    # A função _get_default_options() foi removida.

    def _update_resolution_combobox(self):
        """
        Atualiza os valores da combobox de resolução e define a seleção inicial.
        """
        # Atualiza as opções visíveis na combobox
        self.master.after(0, lambda: self.select_resolution_cbb.configure(values=self.available_formats))

        initial_selection = "Selecione a Resolução"
        if not self.available_formats:
            # Se não houver formatos disponíveis, define uma mensagem e desabilita o botão de download
            initial_selection = "Nenhuma opção disponível"
            self.master.after(0, lambda: self._set_download_ui_state("disabled"))
        else:
            # Seleciona a primeira opção (que será a mais alta devido à ordenação em _filter_formats)
            initial_selection = self.available_formats[0]
            # Garante que a combobox esteja habilitada se houver formatos
            self.master.after(0, lambda: self.select_resolution_cbb.configure(state="readonly"))

        # Define o texto e a seleção na combobox
        self.master.after(0, lambda: self.select_resolution_cbb.set(initial_selection))

    def start_download(self):
        """
        Inicia o processo de download do vídeo/áudio selecionado.
        """
        self.video_url = self.url_input.get().strip()

        if not self.video_info:
            self._write_to_terminal(
                "[ERRO] Nenhuma informação do vídeo/playlist disponível. Por favor, verifique a URL novamente.")
            self._set_ui_state("normal")
            return

        selected_option = self.select_resolution_cbb.get()
        if not selected_option or selected_option == "Selecione a Resolução" or selected_option == "Nenhuma opção disponível":
            self._write_to_terminal("[ERRO] Por favor, selecione uma opção de download (vídeo/áudio) válida.")
            return

        self._set_ui_state("disabled")
        self._write_to_terminal(f"[INFO] Iniciando download para '{selected_option}'...")

        threading.Thread(target=self._process_download, args=(selected_option,)).start()

    def _process_download(self, selected_option):
        """
        Processa o download com base na opção selecionada (vídeo ou áudio).
        """
        try:
            download_type = "video"
            format_selector = ""

            if "Vídeo" in selected_option:
                download_type = "video"
                # Extrai a resolução numérica
                res = re.search(r'(\d+)p', selected_option).group(1)
                # Seleciona o melhor vídeo até a resolução especificada + melhor áudio
                format_selector = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
                # Fallback para caso não encontre uma combinação direta
                format_selector += f'/best[height<={res}][ext=mp4][acodec!=none]/best[height<={res}][acodec!=none]'

            elif "Áudio" in selected_option:
                download_type = "audio"
                # Extrai o bitrate de áudio
                abr = re.search(r'(\d+)kbps', selected_option).group(1)
                # Seleciona o melhor áudio até o bitrate especificado
                format_selector = f'bestaudio[abr<={abr}][ext=m4a]/bestaudio[abr<={abr}]'

            self._download_and_convert(download_type, format_selector, self.video_url, self.video_info)

        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            self._write_to_terminal(f"[ERRO] Erro no processamento: {error_details}")
            self._set_ui_state("normal")
            self._write_to_terminal("[INFO] Pronto para baixar! Insira uma nova URL ou baixe o último vídeo.")

    def _download_and_convert(self, download_type, format_selector, url, info):
        """
        Executa o download e, se necessário, a conversão do arquivo.
        """
        try:
            self._cleanup_temp_folder()

            ydl_opts = {
                'timeout': 60,
                "retries": 10,
                'progress_hooks': [self._download_progress_hook],
                'quiet': True,
                'ignoreerrors': True,
                'format': format_selector,
                'merge_output_format': 'mp4' if download_type == "video" else None,
                'postprocessors': []
            }

            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path
            else:
                self._write_to_terminal(
                    "[AVISO] FFmpeg não configurado. A fusão de vídeo/áudio ou extração de áudio pode falhar.")
                if download_type == "video":
                    self._write_to_terminal(
                        "[ERRO] FFmpeg é necessário para baixar vídeos com áudio nas resoluções selecionadas. Verifique a instalação.")
                    raise RuntimeError("FFmpeg é necessário para esta operação.")

            final_ext = "mp4" if download_type == "video" else "m4a"

            if download_type == "audio":
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '192', # Qualidade preferida para extração de áudio
                })
                final_ext = "m4a"

            target_download_folder = config_manager.download_folder
            if self.is_playlist and self.playlist_title:
                playlist_folder_name = self._sanitize_filename(self.playlist_title)
                target_download_folder = os.path.join(config_manager.download_folder, playlist_folder_name)
                os.makedirs(target_download_folder, exist_ok=True)
                ydl_opts['outtmpl'] = os.path.join(target_download_folder, '%(title)s.%(ext)s')
                ydl_opts['noplaylist'] = False
                self._write_to_terminal(f"[INFO] Baixando para a pasta da playlist: {target_download_folder}")
            else:
                ydl_opts['outtmpl'] = os.path.join(self.temp_folder, '%(title)s.%(ext)s')
                ydl_opts['noplaylist'] = True
                self._write_to_terminal("[INFO] Baixando vídeo individual.")

            with ytdl.YoutubeDL(ydl_opts) as ydl:
                download_info = ydl.extract_info(url)
                if download_info is None:
                    raise ValueError("Falha ao extrair informações do vídeo/playlist durante o download.")

                # Processamento e movimentação do arquivo final para downloads de vídeo individual
                if not self.is_playlist:
                    final_file_path_temp = download_info.get('_filepath')
                    # Tenta obter o caminho do arquivo de diferentes atributos
                    if not final_file_path_temp and download_info.get('requested_downloads'):
                        first_download_entry = download_info['requested_downloads'][0]
                        final_file_path_temp = first_download_entry.get('_filepath')
                        if not final_file_path_temp and first_download_entry.get('filepath'):
                            final_file_path_temp = first_download_entry['filepath']

                    if not final_file_path_temp or not os.path.exists(final_file_path_temp):
                        self._write_to_terminal(
                            "[AVISO] Arquivo final temporário não encontrado diretamente. Tentando encontrar o arquivo mais recente.")
                        # Procura o arquivo mais recente na pasta temporária
                        recent_files = sorted(
                            [os.path.join(self.temp_folder, f) for f in os.listdir(self.temp_folder)
                             if
                             os.path.isfile(os.path.join(self.temp_folder, f)) and not f.endswith(('.part', '.ytdl'))],
                            key=os.path.getmtime, reverse=True
                        )
                        if recent_files:
                            final_file_path_temp = recent_files[0]
                            self._write_to_terminal(f"[INFO] Arquivo mais recente encontrado: {final_file_path_temp}")
                        else:
                            raise FileNotFoundError(
                                f"Arquivo final não encontrado no diretório temporário para '{info.get('title', 'video')}'.")

                    time.sleep(1) # Pequena pausa para garantir que o arquivo esteja pronto

                    title_for_filename = self._sanitize_filename(info.get("title", "video"))
                    destination_path = os.path.join(config_manager.download_folder, f"{title_for_filename}.{final_ext}")

                    # Adiciona contador para evitar sobrescrever arquivos existentes
                    counter = 1
                    original_destination_path = destination_path
                    while os.path.exists(destination_path):
                        name, ext = os.path.splitext(original_destination_path)
                        destination_path = f"{name} ({counter}){ext}"
                        counter += 1

                    shutil.move(final_file_path_temp, destination_path)

                self._write_to_terminal("\n[SUCESSO] Download finalizado!")

        except ytdl.DownloadError as e:
            self._write_to_terminal(f"\n[ERRO] Erro de download: {e}")
            if "ffmpeg" in str(e).lower() and download_type == "video":
                self._write_to_terminal(
                    "[ERRO] O FFmpeg é necessário para combinar vídeo e áudio. Por favor, verifique a instalação do FFmpeg.")
        except FileNotFoundError as e:
            self._write_to_terminal(f"\n[ERRO] Erro de arquivo: {e}")
        except RuntimeError as e:
            self._write_to_terminal(f"\n[ERRO] Operação cancelada: {e}")
        except Exception as ex:
            import traceback
            error_details = traceback.format_exc()
            self._write_to_terminal(f"\n[ERRO] Erro na conversão ou movimentação: {error_details}")
        finally:
            self._cleanup_temp_folder()  # Limpa a pasta temporária
            self._set_ui_state("normal") # Reabilita a UI
            self._write_to_terminal("[INFO] Pronto para baixar! Insira uma nova URL ou baixe o último vídeo.")

    _last_progress_line_index = None # Variável para controlar a linha de progresso no terminal

    def _download_progress_hook(self, d):
        """
        Hook de progresso para o yt-dlp, atualizando a barra de progresso no terminal.
        """
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)

            filename = d.get('filename', 'arquivo desconhecido')
            display_filename = os.path.basename(filename)

            if total_bytes > 0:
                progress = (downloaded_bytes / total_bytes) * 100
                message = f"[PROGRESSO] Baixando '{display_filename}': {progress:.1f}%"
            else:
                message = f"[PROGRESSO] Baixando '{display_filename}'..."

            self.master.after(0, lambda: self._update_progress_line(message))

        elif d['status'] == 'finished':
            self.master.after(0, lambda: self._write_to_terminal("\n[INFO] Download de item concluído, processando..."))
            self._last_progress_line_index = None # Reseta o índice da linha de progresso
        elif d['status'] == 'error':
            filename = d.get('filename', 'arquivo desconhecido')
            self.master.after(0, lambda: self._write_to_terminal(
                f"\n[AVISO] Erro ao baixar '{filename}': {d.get('error', 'Erro desconhecido')}"))
            self._last_progress_line_index = None # Reseta o índice da linha de progresso

    def _update_progress_line(self, message):
        """
        Atualiza a linha de progresso no terminal, sobrescrevendo a anterior.
        """
        self.app_terminal.configure(state="normal")
        if self._last_progress_line_index:
            # Apaga a linha anterior e insere a nova
            self.app_terminal.delete(self._last_progress_line_index, f"{self._last_progress_line_index} lineend")
            self.app_terminal.insert(self._last_progress_line_index, message, "progress_tag")
        else:
            # Insere uma nova linha e armazena seu índice
            self.app_terminal.insert(ctk.END, message + "\n", "progress_tag")
            self._last_progress_line_index = self.app_terminal.index("end-2c linestart")

        self.app_terminal.see(ctk.END) # Rola para o final
        self.app_terminal.configure(state="disabled")

    @staticmethod
    def _sanitize_filename(filename):
        """
        Remove caracteres inválidos de um nome de arquivo.
        """
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def _cleanup_temp_folder(self):
        """
        Limpa o conteúdo da pasta temporária de downloads.
        """
        if os.path.exists(self.temp_folder):
            for filename in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path) # Deleta arquivo
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path) # Deleta pasta
                except Exception as e:
                    self._write_to_terminal(f'[ERRO] Falha ao deletar {file_path}. Razão: {e}')
        os.makedirs(self.temp_folder, exist_ok=True) # Garante que a pasta temporária exista

    def _set_ui_state(self, state):
        """
        Define o estado (normal/disabled) de elementos gerais da UI.
        """
        self.master.after(0, lambda: self.url_input.configure(state=state))
        self.master.after(0, lambda: self.select_save_local_btn.configure(state=state))

        if state == "normal":
            self._set_download_ui_state("normal")
        else:
            self._set_download_ui_state("disabled")

    def _set_download_ui_state(self, state):
        """
        Define o estado (normal/disabled) dos elementos de download (combobox e botão de download).
        A combobox é "readonly" quando habilitada.
        """
        # A combobox é 'readonly' se o estado for 'normal' E houver formatos disponíveis
        self.master.after(0, lambda: self.select_resolution_cbb.configure(
            state="readonly" if state == "normal" and self.available_formats else "disabled"))
        self.master.after(0, lambda: self.download_file_btn.configure(state=state))


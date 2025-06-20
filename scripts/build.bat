@echo off
setlocal

:: Muda para o diretório raiz do repositorio antes de executar PyInstaller
:: Isso garante que todos os caminhos relativos no PyInstaller funcionem a partir da raiz do projeto.
pushd "%~dp0"
cd ..
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel mudar para o diretorio raiz do repositorio. O script pode nao estar na pasta 'scripts'.
    pause
    popd
    exit /b %errorlevel%
)
echo Diretorio atual do script: %~dp0
echo Diretorio raiz do repositorio para PyInstaller: %cd%
echo.

:: Define o nome do seu executável.
set "APP_NAME=Web Downloader"

:: Define o arquivo principal do seu aplicativo (agora relativo a raiz do repo).
set "MAIN_SCRIPT=main.py"

:: Define o ícone do aplicativo para o executável (agora relativo a raiz do repo).
set "APP_ICON=gui/assets/icon.ico"

:: Caminho para a pasta de dependências do FFmpeg (agora relativo a raiz do repo).
set "FFMPEG_DEPENDENCIES_PATH=dependencies/ffmpeg"

:: Mensagem inicial informativa.
echo Iniciando o empacotamento do aplicativo com PyInstaller...
echo.

:: Comando PyInstaller para empacotar o aplicativo.
:: Cada linha terminando com ^ indica que o comando continua na proxima linha.
:: Nao adicione comentarios na mesma linha que um ^, pois podem causar erros no cmd.
pyinstaller %MAIN_SCRIPT% ^
  --name "%APP_NAME%" ^
  --onefile ^
  --windowed ^
  --icon "%APP_ICON%" ^
  --add-data "gui/assets;gui/assets" ^
  --add-data "gui/assets/fonts;gui/assets/fonts" ^
  --add-data "config;config" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/ffmpeg.exe;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/ffprobe.exe;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/ffplay.exe;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/avcodec-61.dll;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/avdevice-61.dll;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/avfilter-10.dll;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/avformat-61.dll;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/avutil-59.dll;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/postproc-58.dll;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/swresample-5.dll;dependencies/ffmpeg" ^
  --add-binary "%FFMPEG_DEPENDENCIES_PATH%/swscale-8.dll;dependencies/ffmpeg" ^
  --clean

:: Verifica o código de saída do PyInstaller para determinar o sucesso ou falha.
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Ocorreu um erro durante o empacotamento com PyInstaller.
    echo Por favor, verifique as mensagens de erro acima para mais detalhes.
) else (
    echo.
    echo Empacotamento concluido com sucesso!
    echo O executavel foi gerado na pasta "dist".
)

echo.
echo Pressione qualquer tecla para sair...
pause > nul

:: Retorna ao diretório original de onde o script foi executado
popd
endlocal
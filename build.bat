@echo off
setlocal

:: Define o nome do seu executável
set APP_NAME="Web Downloader"

:: Define o arquivo principal do seu aplicativo
set MAIN_SCRIPT="main.py"

:: Define o ícone do aplicativo
set APP_ICON="icon.ico"

:: Mensagem inicial
echo Iniciando o empacotamento do aplicativo com PyInstaller...
echo.

:: Comando PyInstaller
:: Os ^ (circumflexos) no final de cada linha são para quebrar o comando em varias linhas, mantendo-o legivel.
:: Nao remova-os exceto na ultima linha do comando PyInstaller.
pyinstaller %MAIN_SCRIPT% ^
  --name %APP_NAME% ^
  --onefile ^
  --icon %APP_ICON% ^
  --add-data "%APP_ICON%;." ^
  --add-data "fonts;fonts" ^
  --add-binary "dependencies/ffmpeg.exe;." ^
  --add-binary "dependencies/ffprobe.exe;." ^
  --add-binary "dependencies/yt-dlp.exe;." ^
  --clean

:: Verifica se o PyInstaller foi executado com sucesso
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Ocorreu um erro durante o empacotamento com PyInstaller.
    echo Verifique as mensagens acima para detalhes.
) else (
    echo.
    echo Empacotamento concluido com sucesso!
    echo O executavel esta na pasta "dist".
)

echo.
echo Pressione qualquer tecla para sair...
pause > nul
endlocal

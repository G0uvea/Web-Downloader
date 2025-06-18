#!/bin/bash

# Define o nome do seu executável
APP_NAME="Web Downloader"

# Define o arquivo principal do seu aplicativo
MAIN_SCRIPT="main.py"

# Define o ícone do aplicativo
APP_ICON="icon.ico"

# Mensagem inicial
echo "Iniciando o empacotamento do aplicativo com PyInstaller..."
echo ""

# Comando PyInstaller
# Os \ (backslashes) no final de cada linha sao para quebrar o comando em varias linhas, mantendo-o legivel.
# Nao remova-os exceto na ultima linha do comando PyInstaller.
pyinstaller "$MAIN_SCRIPT" \
  --name "$APP_NAME" \
  --onefile \
  --windowed \
  --icon "$APP_ICON" \
  --add-data "$APP_ICON:." \
  --add-data "fonts:fonts" \
  --add-data "src:src"

# Verifica se o PyInstaller foi executado com sucesso
if [ $? -ne 0 ]; then
    echo ""
    echo "ERRO: Ocorreu um erro durante o empacotamento com PyInstaller."
    echo "Verifique as mensagens acima para detalhes."
else
    echo ""
    echo "Empacotamento concluido com sucesso!"
    echo "O executavel esta na pasta \"dist\"."
fi

echo ""
echo "Pressione Enter para sair..."
read -n 1 -s
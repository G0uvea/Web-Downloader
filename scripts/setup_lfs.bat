@echo on
echo CUIDADO: Este script fara um commit e push forcados, o que pode sobrescrever o historico remoto.
echo Use com extrema cautela!

REM Pergunta ao usuario se ele realmente deseja continuar
set /p proceed="Tem certeza que deseja continuar? (s/n): "
if /i "%proceed%" neq "s" (
    echo Operacao cancelada.
    pause
    exit /b 1
)

echo.
echo Determinando o diretorio raiz do repositorio...
REM Navega para o diretorio onde o script esta
pushd "%~dp0"
echo Diretorio atual do script: %cd%

REM Navega para a raiz do repositorio (um nivel acima de 'scripts')
cd ..
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel subir um diretorio. O script pode nao estar na pasta 'scripts'.
    pause
    popd
    exit /b %errorlevel%
)
set "REPO_ROOT_DIR=%cd%"
echo Diretorio raiz do repositorio: %REPO_ROOT_DIR%
pause

REM Agora que estamos na raiz, o resto dos comandos funcionarao corretamente.
REM Nao precisamos mais do 'cd /d "D:\Projetos HDD\Python Projects\Web-Downloader"' absoluto

echo.
echo Configurando Git LFS, adicionando, comitando e enviando para o GitHub (branch 'main')...

REM Garante que o Git LFS esteja instalado e configurado, e força a atualizacao de hooks
echo.
echo Executando 'git lfs update --force' para garantir a configuracao do LFS...
git lfs update --force
if %errorlevel% neq 0 (
    echo ERRO: Falha ao configurar o Git LFS com 'git lfs update --force'. Certifique-se de que o Git LFS esta instalado.
    pause
    popd
    exit /b %errorlevel%
)
echo Git LFS configurado e hooks atualizados.
pause

REM Adiciona os arquivos .gitattributes ao stage
echo.
echo Adicionando .gitattributes ao stage...
git add .gitattributes
if %errorlevel% neq 0 (
    echo ERRO: Falha ao adicionar .gitattributes.
    pause
    popd
    exit /b %errorlevel%
)
pause

REM Adiciona os arquivos especificados em .gitattributes ao stage
echo.
echo Adicionando arquivos .dll e .exe de dependencies/ffmpeg ao stage...
git add dependencies/ffmpeg/*.dll
if %errorlevel% neq 0 (
    echo ERRO: Falha ao adicionar arquivos .dll.
    pause
    popd
    exit /b %errorlevel%
)
git add dependencies/ffmpeg/*.exe
if %errorlevel% neq 0 (
    echo ERRO: Falha ao adicionar arquivos .exe.
    pause
    popd
    exit /b %errorlevel%
)
pause

echo.
echo Verificando status do Git LFS (arquivos rastreados):
git lfs track
pause

echo.
echo Verificando o status atual do Git:
git status
pause

REM Tenta commitar as mudanças. Se nao houver mudancas, o commit pode falhar.
REM Adicionado 'git add .' para garantir que tudo esteja no stage antes do commit.
echo.
echo Adicionando todas as mudancas ao stage (apenas por seguranca)...
git add .
pause

echo.
echo Comitando todas as mudancas. Se ja houver um commit e for apenas para alterar a mensagem ou adicionar algo, use '--amend'.
echo Caso contrario, um novo commit sera criado.
git commit -m "Commit forcado para configuracao de LFS e arquivos binarios"
if %errorlevel% neq 0 (
    echo AVISO: Nenhuma mudanca para comitar ou falha no commit. Tentando commit vazio ou revisando o ultimo.
    git commit --allow-empty -m "Commit forcado para configuracao de LFS e arquivos binarios (vazio)"
    if %errorlevel% neq 0 (
        echo ERRO: Falha critica no commit. O script nao pode prosseguir.
        pause
        popd
        exit /b %errorlevel%
    )
)
pause

REM Envia para o GitHub, FORCANDO para a branch 'main'
echo.
echo ENVIANDO PARA O GITHUB (PUSH FORCADO)!
echo Isso sobrescrevera o historico remoto. Pense bem antes de continuar.
git push origin main --force-with-lease
if %errorlevel% neq 0 (
    echo ERRO: Falha ao enviar para o GitHub (push forcado). Verifique sua conexao e credenciais.
    echo Se o push falhar repetidamente, pode ser necessario resolver conflitos de forma manual ou usar 'git push origin main --force' (mais perigoso).
    pause
    popd
    exit /b %errorlevel%
)

echo.
echo PROCESSO CONCLUIDO! Git LFS configurado, arquivos adicionados, comitados e enviados para o GitHub (push forcado) na branch 'main'.
pause

REM Retorna ao diretorio original de onde o script foi executado
popd
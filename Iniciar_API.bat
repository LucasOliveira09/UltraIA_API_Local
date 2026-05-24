@echo off
title UltraIA API
echo Iniciando a API UltraIA...

cd /d "%~dp0"

:: Ativa o ambiente virtual, se ele existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Aviso: Ambiente virtual 'venv' nao encontrado. Executando com o Python do sistema.
)

:: Executa o programa principal
python main.py

echo.
echo =========================================
echo Processo finalizado! Pode fechar a janela.
pause

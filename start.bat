@echo off
title YouTube Trend & Content Founder
echo ===================================================
echo   YouTube Trend & Content Founder - Inicializando
echo ===================================================
cd /d "%~dp0"

echo [1/2] Verificando dependencias necessarias...
python -m pip install -r requirements.txt --quiet --no-warn-script-location

echo [2/2] Iniciando o servidor e abrindo o navegador...
python run.py
pause

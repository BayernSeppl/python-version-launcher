@echo off
setlocal
cd /d "%~dp0"
title LottoPro - EXE erstellen

echo ============================================
echo   LottoPro Analyse - Windows EXE-Build
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo FEHLER: Python 3 wurde nicht gefunden.
    echo Installiere Python von python.org und aktiviere "Add Python to PATH".
    pause
    exit /b 1
)

if not exist "lotto_app.py" (
    echo FEHLER: lotto_app.py fehlt im Projektordner.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Erstelle eine isolierte Python-Umgebung...
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)

set "PYTHON=.venv\Scripts\python.exe"
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto :error
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 goto :error

if exist build rmdir /s /q build
if exist "dist\LottoPro.exe" del /q "dist\LottoPro.exe"
"%PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed --name LottoPro lotto_app.py
if errorlevel 1 goto :error

if not exist "dist\LottoPro.exe" goto :error

echo.
echo Build erfolgreich!
echo Die EXE befindet sich unter:
echo %~dp0dist\LottoPro.exe
echo.
start "" explorer "%~dp0dist"
pause
exit /b 0

:error
echo.
echo FEHLER beim Build. Pruefe die Fehlermeldung oben.
pause
exit /b 1

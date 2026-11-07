@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo Lotto Pro EXE wird erstellt
echo ========================================

where py >nul 2>nul
if errorlevel 1 (
    echo FEHLER: Python wurde nicht gefunden. Bitte Python 3 installieren und beim Setup "Add Python to PATH" aktivieren.
    pause
    exit /b 1
)

py -3 -m pip install --upgrade pip
if errorlevel 1 goto :error
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :error
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name LottoPro lotto_app.py
if errorlevel 1 goto :error

echo.
echo Fertig! Die Datei liegt hier:
echo %~dp0dist\LottoPro.exe
pause
exit /b 0

:error
echo.
echo FEHLER beim Erstellen. Bitte die Meldung oben pruefen.
pause
exit /b 1

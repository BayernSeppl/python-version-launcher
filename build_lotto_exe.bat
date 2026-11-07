@echo off
setlocal
cd /d "%~dp0"
title LottoPro - Windows EXE erstellen

echo ============================================
echo   LottoPro Analyse - EXE-Build
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 wurde nicht gefunden.
  echo Installiere Python von python.org und aktiviere "Add Python to PATH".
  pause
  exit /b 1
)

py -3 -c "import tkinter" >nul 2>nul
if errorlevel 1 (
  echo Python wurde gefunden, aber Tkinter fehlt. Installiere Python mit Tcl/Tk-Unterstuetzung.
  pause
  exit /b 1
)

py -3 -m pip install --upgrade pip
if errorlevel 1 goto :error
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :error
if exist build rmdir /s /q build
if exist dist\LottoPro.exe del /q dist\LottoPro.exe
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name LottoPro lotto_app.py
if errorlevel 1 goto :error

if not exist dist\LottoPro.exe goto :error

echo.
echo Build erfolgreich!
echo EXE: %~dp0dist\LottoPro.exe
start "" explorer "%~dp0dist"
pause
exit /b 0

:error
echo.
echo FEHLER: Build fehlgeschlagen. Pruefe die Fehlermeldung oben.
pause
exit /b 1

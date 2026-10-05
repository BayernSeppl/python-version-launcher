@echo off
setlocal enabledelayedexpansion

cls
color 0A

echo ======================================================
echo    Python Version Launcher (Batch)
echo ======================================================
echo.
echo Wähle die Python-Version:
echo 1) Python 3.8
echo 2) Python 3.11
echo 3) Python 3.14
echo 0) Abbrechen
echo.
set /p choice="Deine Wahl: "

if "%choice%"=="1" (
    set PYVER=3.8
) else if "%choice%"=="2" (
    set PYVER=3.11
) else if "%choice%"=="3" (
    set PYVER=3.14
) else if "%choice%"=="0" (
    echo Abbruch.
    exit /b 0
) else (
    echo Falsche Auswahl.
    pause
    exit /b 1
)

echo.
echo Bitte gib den Pfad zur Python-Datei an, z.B.:
echo j:\ChatGPT\Wichtige Tools\sitemap-xml-generator\app.py
echo.
set /p SCRIPT="Pfad: "

if not exist "%SCRIPT%" (
    echo Fehler: Datei nicht gefunden: %SCRIPT%
    pause
    exit /b 1
)

echo.
echo Starte mit Python %PYVER%: %SCRIPT%
py -%PYVER% "%SCRIPT%"

if errorlevel 1 (
    echo.
    echo Fehler: Python %PYVER% konnte nicht gestartet werden.
    echo Stelle sicher, dass diese Version installiert ist.
    pause
    exit /b 1
)

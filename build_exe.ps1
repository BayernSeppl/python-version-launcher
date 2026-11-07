@echo off
py -m pip install --upgrade pip
py -m pip install pyinstaller
py -m PyInstaller --onefile --windowed --name LottoPro --clean lotto_app.py
if exist dist\LottoPro.exe (
    echo.
    echo EXE erstellt: dist\LottoPro.exe
) else (
    echo.
    echo Build abgeschlossen, aber EXE wurde nicht gefunden.
)
pause

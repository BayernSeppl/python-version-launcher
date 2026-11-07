$ErrorActionPreference = "Stop"
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt
py -3 -m PyInstaller --onefile --windowed --name LottoPro --clean lotto_app.py
if (Test-Path "dist\LottoPro.exe") {
    Write-Host ""
    Write-Host "EXE erstellt: dist\LottoPro.exe"
} else {
    Write-Host ""
    Write-Host "Build abgeschlossen, aber EXE wurde nicht gefunden."
}
Read-Host "Druecke ENTER zum Beenden"

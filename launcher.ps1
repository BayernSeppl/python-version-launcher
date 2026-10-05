$ErrorActionPreference = 'Stop'

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "    Python Version Launcher (PowerShell)" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wähle die Python-Version:"
Write-Host "  [1] Python 3.8"
Write-Host "  [2] Python 3.11"
Write-Host "  [3] Python 3.14"
Write-Host "  [0] Abbrechen"
Write-Host ""
$choice = Read-Host "Deine Wahl"

switch ($choice) {
    '1' { $pyVersion = '3.8' }
    '2' { $pyVersion = '3.11' }
    '3' { $pyVersion = '3.14' }
    '0' { Write-Host "Abbruch."; exit 0 }
    default { Write-Host "Falsche Auswahl." -ForegroundColor Red; exit 1 }
}

Write-Host ""
Write-Host "Bitte den Pfad zur Python-Datei eingeben, z.B.:"
Write-Host "j:\ChatGPT\Wichtige Tools\sitemap-xml-generator\app.py"
$scriptPath = Read-Host "Pfad"

if (-not (Test-Path $scriptPath)) {
    Write-Host "Fehler: Datei nicht gefunden: $scriptPath" -ForegroundColor Red
    Read-Host "Enter zum Beenden"
    exit 1
}

Write-Host ""
Write-Host "Starte mit Python $pyVersion: $scriptPath" -ForegroundColor Green
& py -$pyVersion $scriptPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "Fehler beim Start mit Python $pyVersion" -ForegroundColor Red
    Read-Host "Enter zum Beenden"
    exit 1
}

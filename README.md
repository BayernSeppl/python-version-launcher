# LottoPro Analyse

Eine Windows-GUI-App für Lotto 6 aus 49 und Build-Skripte für die Programme in diesem Repository.

## EXE-Dateien unter Windows erstellen

Voraussetzung ist Python 3.10 oder neuer. Beim Installieren von Python die Option **Add Python to PATH** aktivieren. Dann im Datei-Explorer den Repository-Ordner öffnen und die gewünschte BAT-Datei doppelklicken:

- `build_lotto_exe.bat` erstellt `dist\LottoPro.exe`.
- `build_launcher_gui_exe.bat` erstellt `dist\PythonVersionLauncher.exe`.
- `build_launcher_projects_exe.bat` erstellt `dist\ProjektLauncher.exe`.
- `build_all_exes.bat` erstellt alle drei Dateien.

Die BAT-Dateien installieren PyInstaller automatisch. Eine Internetverbindung ist beim ersten Build erforderlich. Build-Ausgaben und EXE-Dateien werden im Ordner `dist` abgelegt.

Die beiden Launcher-Programme starten externe Python-Skripte; deren Nutzung setzt weiterhin eine passende Python-Installation auf dem Zielrechner voraus. Die Lotto-App kann dagegen als eigenständige EXE gebaut werden.

## Lotto-App

Die Lotto-App bietet Demo-Daten, CSV-Import, einfache Filter für Tipp-Sätze und CSV-Export. Historische Daten können keine zukünftigen Ziehungen vorhersagen und keine Gewinne garantieren.

Zum direkten Starten mit installiertem Python:

```bat
py -3 lotto_app.py
```

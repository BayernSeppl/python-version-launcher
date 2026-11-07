# LottoPro Analyse

Eine kleine Windows-GUI-App für Lotto 6 aus 49 mit:

- statistischer Auswertung historischer Ziehungen
- Filterung nach Summe, Gerade/Ungerade, Häufigkeit
- Erstellung mehrerer Tipp-Sätze
- Export als CSV
- Demo-Daten ohne externe Dateien

Wichtig: Die App analysiert historische Daten und erzeugt Kombinationen anhand von Mustern in zuvor gezogenen Zahlen. Sie kann keine zukünftigen Lotto-Ergebnisse vorhersagen oder Gewinne garantieren.

## Voraussetzungen

- Python 3.11 (empfohlen)
- Windows 10/11

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install pyinstaller
```

## App starten

```bash
python lotto_app.py
```

## EXE bauen

Windows CMD:

```bat
build_exe.bat
```

PowerShell:

```powershell
.\build_exe.ps1
```

Die erzeugte EXE liegt anschließend im Ordner `dist\`.

## Hinweis

Das Programm verwendet historische Ziehungen nur als Analyse- und Organisationswerkzeug. Es ersetzt kein Glücksspiel- oder Gewinnsystem und kann keine zukünftigen Zahlen sicher bestimmen.

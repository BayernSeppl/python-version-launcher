# LottoPro Analyse

Eine kleine Windows-GUI-App für Lotto 6 aus 49 mit:

- statistischer Auswertung historischer Ziehungen
- Filterung nach Summe, Gerade/Ungerade
- Erstellung mehrerer Tipp-Sätze
- Export als CSV
- Demo-Daten ohne externe Dateien

Wichtig: Das Programm analysiert historische Zahlenmuster und hilft beim Organisieren von Tipp-Sätzen. Es kann keine zukünftigen Lotto-Ergebnisse vorhersagen und keine Gewinne garantieren.

## Voraussetzungen

- Windows 10/11
- Python 3.11 (empfohlen)

## Installation

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## App starten

```powershell
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

Die EXE entsteht dann im Ordner `dist\`.

## Hinweis

Dieses Tool dient zur Analyse historischer Lotto-Daten und zur Erstellung von Organisations- und Filtervorschlägen. Es ersetzt keine statistische Garantien für zukünftige Gewinne.


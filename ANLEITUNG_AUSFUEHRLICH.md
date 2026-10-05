# Python Launcher - Komplette Schritt-für-Schritt Anleitung

## 1) Warum du einen Launcher brauchst

Du hast auf deinem Computer mehrere Python-Versionen installiert:

- Python 3.8
- Python 3.11
- Python 3.14

Nicht jedes Programm funktioniert mit jeder Version. Einige Programme brauchen genau eine bestimmte Python-Version.

Das ist genau der Grund, warum du jetzt einen Launcher brauchst: damit du für jedes Programm die passende Python-Version sauber auswählen kannst.

Für deine Sitemap-Tools ist in der Regel Python 3.11 die beste Wahl.

---

## 2) Was ist in dem ZIP-Ordner enthalten?

In der ZIP-Datei findest du diese Dateien:

- launcher.bat
- launcher.ps1
- launcher_gui.py
- launcher_projects.py
- README.md
- ANLEITUNG.md

Das ist alles, was du zum Starten brauchst.

Du brauchst keine zusätzlichen Dateien zu installieren.

---

## 3) Wo du den Ordner ablegen solltest

Am besten so:

```text
j:\ChatGPT\Wichtige Tools\Python-Launcher und CO\
```

In diesem Ordner musst du die entpackten Dateien liegen lassen.

---

## 4) Was du nach dem Entpacken sehen solltest

Der Ordner sollte ungefähr so aussehen:

```text
j:\ChatGPT\Wichtige Tools\
├── Python-Launcher und CO\
│   ├── launcher.bat
│   ├── launcher.ps1
│   ├── launcher_gui.py
│   ├── launcher_projects.py
│   ├── README.md
│   └── ANLEITUNG.md
│
├── sitemap-xml-generator\
│   ├── app.py
│   ├── requirements.txt
│   ├── templates\
│   └── run.bat
│
└── sitemap-submission-tool\
    ├── app.py
    ├── requirements.txt
    ├── templates\
    └── run.bat
```

---

## 5) Die einfachste Methode: launcher_projects.py

Diese Version ist für dich am sinnvollsten.

### So startest du sie:

1. Öffne PowerShell
2. Gehe in den Launcher-Ordner:

```powershell
cd j:\ChatGPT\Wichtige Tools\Python-Launcher und CO
```

3. Starte den Launcher:

```powershell
py -3.11 launcher_projects.py
```

Oder du machst einen Doppelklick auf `launcher_projects.py`.

---

## 6) Wie du das Projekt auswählst

Wenn das Fenster geöffnet ist, siehst du:

- Projekt auswählen
- Ordner auswählen
- Python-Version wählen
- Projekt starten

### Beispiel für dein Sitemap-Tool

1. Wähle `Sitemap XML Generator`
2. Klicke auf `Ordner auswählen`
3. Navigiere zu:

```text
j:\ChatGPT\Wichtige Tools\sitemap-xml-generator
```

4. Wähle den Ordner
5. Wähle Python `3.11`
6. Klicke auf `Projekt starten`

Dann startet dein Tool mit der richtigen Python-Version.

---

## 7) Welche Python-Version du normalerweise verwenden solltest

### Python 3.11
Das ist für die meisten deiner Tools die beste Wahl.

- modern
- stabil
- kompatibel mit Flask
- kompatibel mit Requests
- kompatibel mit BeautifulSoup

Für deine Sitemap-Tools: 3.11 = empfohlen

### Python 3.8
Für ältere Programme, die wirklich 3.8 brauchen.

### Python 3.14
Nur für Programme, die genau diese Version benötigen.

Nicht automatisch für alle Programme nutzen.

---

## 8) Die Batch-Version: launcher.bat

Diese Variante ist sehr einfach.

### So startest du sie:

1. Doppelklick auf `launcher.bat`
2. Menü erscheint
3. Wähle deine Python-Version
4. Gib den Pfad zur Datei ein
5. Das Programm startet

### Beispiel:

```text
j:\ChatGPT\Wichtige Tools\sitemap-xml-generator\app.py
```

---

## 9) Die PowerShell-Version: launcher.ps1

### So startest du sie:

```powershell
powershell -ExecutionPolicy Bypass -File launcher.ps1
```

Oder:
- Rechtsklick auf die Datei
- Als Administrator ausführen

Diese Variante ist gut, wenn du mehr Kontrolle oder Fehlerausgaben brauchst.

---

## 10) Die GUI-Version: launcher_gui.py

Diese Variante ist sehr einfach zu bedienen.

### Starten:

```powershell
py -3.11 launcher_gui.py
```

Danach kannst du:

- die Python-Version auswählen
- die Datei per Durchsuchen wählen
- das Programm starten

---

## 11) So prüfst du, ob Python installiert ist

Gib in PowerShell ein:

```powershell
py -3.11 --version
```

Wenn du eine Ausgabe wie diese siehst:

```text
Python 3.11.x
```

dann ist alles richtig.

---

## 12) Häufige Fehler und Lösungen

### Fehler 1: `py` wird nicht erkannt

**Ursache:**
- Python ist nicht installiert oder nicht im PATH

**Lösung:**
- Python neu installieren
- Bei der Installation auf `Add Python to PATH` achten
- Computer neu starten

---

### Fehler 2: `ModuleNotFoundError: No module named 'flask'`

**Ursache:**
- Flask ist nicht installiert

**Lösung:**

Im Projektordner:

```powershell
pip install -r requirements.txt
```

Oder in einer virtuellen Umgebung:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

---

### Fehler 3: `Datei nicht gefunden`

**Ursache:**
- Falscher Pfad
- app.py nicht im richtigen Ordner

**Lösung:**
- Den ordentlichen Projektordner auswählen
- Sicherstellen, dass `app.py` wirklich dort liegt

---

### Fehler 4: Port schon belegt

**Ursache:**
- Ein anderes Programm nutzt den Port bereits

**Lösung:**
- Das andere Programm schließen
- Oder den Port im Code ändern

---

## 13) So installierst du Python 3.11 korrekt

### Download

Gehe zu:

https://www.python.org/downloads/

Lade die passende 3.11-Version herunter.

### Installation

1. Die EXE-Datei ausführen
2. `Add Python to PATH` aktivieren
3. `Install Now` klicken
4. Fertig

---

## 14) Was ist für deine Sitemap-Tools die beste Auswahl?

Für deine Projektevon `Sitemap XML Generator` und `Sitemap Submission Tool`:

- Python 3.11
- `launcher_projects.py`
- Projektordner auswählen
- Starten

Das ist die beste Kombination.

---

## 15) Meine Empfehlung für dich

Nutze diese Reihenfolge:

1. Python 3.11 installieren
2. Launcher-Ordner entpacken
3. `launcher_projects.py` starten
4. Projekt auswählen
5. Ordner auswählen
6. Python 3.11 wählen
7. Starten

Das ist der beste und sauberste Weg.

---

## 16) Fazit

Du hast jetzt:

- einen kompletten Launcher
- mehrere Varianten zur Auswahl
- alles, was du für Python-Versionen brauchst
- eine einfache und sichere Lösung für dein Problem

Das wichtigste: Für deine Sitemap-Tools sollte immer Python 3.11 verwendet werden.

Wenn du die Dateien in dem richtigen Ordner hast, brauchst du nichts mehr zu kopieren.

Du bist damit komplett vorbereitet.

---

## 17) Nächster Schritt

Starte jetzt:

```powershell
cd j:\ChatGPT\Wichtige Tools\Python-Launcher und CO
py -3.11 launcher_projects.py
```

Dann wählst du dein Projekt und startest es mit der richtigen Version.

Viel Erfolg! ✅

# Python Launcher - Komplette Anleitung

## Ordnerstruktur

```
j:\ChatGPT\Wichtige Tools\Python-Launcher und CO\
├── launcher.bat
├── launcher.ps1
├── launcher_gui.py
├── launcher_projects.py
└── ANLEITUNG.md (diese Datei)
```

## Was ist dieser Launcher?

Dieser Launcher hilft dir, Python-Programme mit der richtigen Python-Version zu starten.

Du hast mehrere Python-Versionen installiert:
- Python 3.8 (alte Programme)
- Python 3.11 (moderne Programme)
- Python 3.14 (neue Programme)

Dieser Launcher wählt die passende Version automatisch oder auf Wunsch manuell.

## Die 4 verschiedenen Launcher-Varianten

### 1. launcher.bat (Windows Batch)

**Verwendung:**
- Doppelklick auf `launcher.bat`

**Vorteil:**
- Schnell und einfach
- Keine Zusatzsoftware nötig

**Funktion:**
- Menü zum Auswählen der Python-Version
- Du gibst den Pfad zur Python-Datei ein
- Programm startet mit der gewählten Version

**Beispiel:**
```
j:\ChatGPT\Wichtige Tools\sitemap-xml-generator\app.py
```

---

### 2. launcher.ps1 (PowerShell)

**Verwendung:**
```powershell
powershell -ExecutionPolicy Bypass -File launcher.ps1
```

Oder: Rechtsklick → "Mit PowerShell ausführen"

**Vorteil:**
- Bessere Fehlerbehandlung als Batch
- Farbige Ausgabe

**Funktion:**
- Menü zum Auswählen der Python-Version
- Du gibst den Pfad zur Python-Datei ein
- Programm startet mit der gewählten Version

---

### 3. launcher_gui.py (Grafische Oberfläche - einfach)

**Verwendung:**
```cmd
py -3.11 launcher_gui.py
```

Oder im Windows Explorer:
- Doppelklick auf `launcher_gui.py`

**Vorteil:**
- Grafisches Menü
- Benutzerfreundlich
- "Durchsuchen"-Button zum Ordner auswählen

**Funktion:**
1. Wähle die Python-Version (Dropdown)
2. Gib den Pfad zur Python-Datei ein oder nutze "Durchsuchen"
3. Klicke "Programm starten"

---

### 4. launcher_projects.py (Grafische Oberfläche - mit Projekten)

**Verwendung:**
```cmd
py -3.11 launcher_projects.py
```

Oder im Windows Explorer:
- Doppelklick auf `launcher_projects.py`

**Vorteil:**
- Eigenes Menü für deine Projekte
- Vordefinierte Projekte (Sitemap Generator, Submission Tool)
- Du musst nur noch Ordner auswählen und starten

**Funktion:**
1. Wähle ein Projekt aus dem Dropdown
2. Klicke "Ordner auswählen" und wähle den Projektordner
3. Wähle die Python-Version (normalerweise 3.11)
4. Klicke "Projekt starten"

---

## Empfohlene Ordnerstruktur

```
j:\ChatGPT\Wichtige Tools\
├── Python-Launcher und CO\
│   ├── launcher.bat
│   ├── launcher.ps1
│   ├── launcher_gui.py
│   ├── launcher_projects.py
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

## So nutzt du den Launcher für deine Projekte

### Mit launcher_projects.py (EMPFOHLEN)

1. Öffne PowerShell oder CMD
2. Navigiere zum Launcher-Ordner:
   ```cmd
   cd j:\ChatGPT\Wichtige Tools\Python-Launcher und CO
   ```
3. Starte den Launcher:
   ```cmd
   py -3.11 launcher_projects.py
   ```
4. Ein Fenster öffnet sich
5. Wähle aus dem Dropdown:
   - "Sitemap XML Generator" oder
   - "Sitemap Submission Tool"
6. Klicke "Ordner auswählen"
7. Navigiere zu z. B.:
   ```
   j:\ChatGPT\Wichtige Tools\sitemap-xml-generator
   ```
8. Bestätige mit OK
9. Wähle die Python-Version (normalerweise 3.11)
10. Klicke "Projekt starten"

Das Projekt startet dann mit der richtigen Python-Version!

---

## Python-Versionen - Welche nutzen?

### Python 3.8
- Für sehr alte Programme
- Eher selten nötig

### Python 3.11 ✅ EMPFOHLEN für deine Tools
- Für moderne Programme
- Am meisten kompatibel
- Flask, BeautifulSoup, Requests funktionieren problemlos
- **Für Sitemap-Tools: Immer 3.11 nutzen!**

### Python 3.14
- Für neue Programme
- Manche Packages sind noch nicht kompatibel
- Nur wenn ein Programm das explizit verlangt

---

## Häufige Probleme und Lösungen

### "Python konnte nicht gefunden werden"

**Ursache:**
- Python ist nicht im PATH installiert
- Die angegebene Version ist nicht installiert

**Lösung:**
1. Python neu installieren
2. **Wichtig:** Bei der Installation "Add Python to PATH" ankreuzen
3. Computer neustarten
4. Versuche es erneut

---

### "Datei nicht gefunden"

**Ursache:**
- Der Pfad ist falsch geschrieben
- Die Datei existiert nicht

**Lösung:**
1. Nutze den "Durchsuchen"-Button
2. Oder gib den kompletten Pfad ein, z. B.:
   ```
   j:\ChatGPT\Wichtige Tools\sitemap-xml-generator\app.py
   ```

---

### "ModuleNotFoundError: No module named 'flask'"

**Ursache:**
- Die Python-Module sind nicht installiert
- requirements.txt wurde nicht installiert

**Lösung:**
1. Öffne PowerShell im Projektordner
2. Aktiviere die virtuelle Umgebung:
   ```cmd
   venv\Scripts\activate
   ```
3. Installiere die Module:
   ```cmd
   pip install -r requirements.txt
   ```
4. Starte dann über den Launcher

---

## Weitere Tipps

### Verknüpfung erstellen (Desktop)

Falls du den Launcher häufig brauchst:

1. Rechtsklick auf launcher_projects.py
2. "Verknüpfung erstellen"
3. Verknüpfung auf den Desktop ziehen
4. Doppelklick startet den Launcher sofort

### Mehrere Projekte hinzufügen

Wenn du mehr Projekte hast, kannst du `launcher_projects.py` bearbeiten:

1. Öffne die Datei mit einem Texteditor
2. Füge dein Projekt in das `PROJECTS`-Dictionary ein
3. Beispiel:
   ```python
   "Mein neues Projekt": {
       "script": "app.py",
       "path": "",
       "default_version": "3.11"
   },
   ```
4. Speichern und neu starten

---

## Zusammenfassung

✅ **Für dich mit Sitemap-Tools:**
1. Nutze `launcher_projects.py`
2. Wähle das Projekt
3. Wähle den Ordner
4. Nutze Python 3.11
5. Klicke "Starten"

Fertig! 🎉

# FAQ Studio Premium

FAQ Studio Premium ist eine benutzerfreundliche Desktop-App für Windows, macOS und Linux. Sie läuft lokal mit Python und Tkinter. Erstelle eine gestaltete FAQ-Seite, verwalte Fragen und Antworten, importiere Tabellen und exportiere fertige Inhalte.

## Starten

```bash
python faq_studio_premium.py
```

Windows:

```bat
py faq_studio_premium.py
```

Python 3.10+ empfohlen. Für XLSX-/XLSM-Import einmalig das optionale Excel-Paket installieren:

```bash
python -m pip install -r requirements-faq.txt
```

CSV, HTML, Markdown und JSON funktionieren ohne zusätzliche Pakete.

## Premium-Funktionen

- Übersichtlich gestaltete Desktop-Oberfläche mit Live-Vorschau
- Seitentitel, Marke, Einleitung, Kontakt-Link und frei wählbare Akzentfarbe
- Fragen kategorisieren, durchsuchen und nach Kategorie filtern
- Erkennung sehr ähnlicher Fragen beim Speichern
- Import aus CSV, XLSX und XLSM; deutsche und englische Spaltennamen werden unterstützt
- Antwortvorlagen für freundliche, kurze, Schritt-für-Schritt-, Support- und Versandantworten
- KI-Prompt-Erstellung in die Zwischenablage: der Prompt wird nicht automatisch an einen Dienst gesendet
- Responsive, eigenständige HTML-Datei mit FAQ-Suche, aufklappbaren Antworten und FAQPage-JSON-LD
- Export als HTML, Markdown, CSV oder JSON
- Projekte lokal als JSON speichern und wieder öffnen

## CSV-Import

Die erste Zeile enthält Überschriften. Frage und Antwort sind erforderlich; Kategorie ist optional. Beispiel:

```csv
Kategorie;Frage;Antwort
Versand;Wie lange dauert die Lieferung?;Die voraussichtliche Lieferzeit wird im Checkout angezeigt.
Support;Wie erreiche ich euch?;Nutze bitte unser Kontaktformular.
```

Akzeptierte Spaltennamen: `Kategorie`/`Category`, `Frage`/`Question`, `Antwort`/`Answer`. Excel-Dateien werden aus dem ersten Tabellenblatt gelesen.

## Veröffentlichung

Klicke auf **Website exportieren**, speichere die HTML-Datei und öffne sie im Browser zur Kontrolle. Die Datei enthält Layout, Suche und FAQPage-Strukturdaten und kann danach auf einem Webserver veröffentlicht werden. Der Kontakt-Link wird nur angezeigt, wenn er eingetragen ist.

KI-Vorlagen formulieren keine überprüften Tatsachen. Prüfe Inhalte, Preise, Lieferzeiten und rechtliche Aussagen vor der Veröffentlichung.

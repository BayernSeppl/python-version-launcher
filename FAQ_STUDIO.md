# FAQ Studio

Ein einfach bedienbarer, deutschsprachiger FAQ-Generator für Windows, macOS und Linux. Das Tool läuft lokal mit Python und Tkinter; deine Inhalte werden nicht automatisch an einen Server übertragen.

## Starten

Python 3.10 oder neuer wird empfohlen. Tkinter ist bei vielen Python-Installationen bereits enthalten.

```bash
python faq_generator.py
```

Unter Windows alternativ:

```bat
py faq_generator.py
```

## Funktionen

- Fragen und Antworten erstellen, bearbeiten, löschen, kategorisieren und durchsuchen
- Live-Vorschau und sofort nutzbare Beispieldaten
- CSV-Import mit Spalten wie `Kategorie;Frage;Antwort` (auch englische Spaltennamen `category;question;answer`)
- XLSX-/XLSM-Import aus dem ersten Tabellenblatt; die erste Zeile enthält Überschriften
- Export als barrierearm bedienbare, einklappbare HTML-FAQ, Markdown, CSV oder JSON
- Projekte lokal als JSON speichern und später wieder öffnen
- Antwortvorlagen für freundliche, kurze, Schritt-für-Schritt-, Support- und Kauf-/Versand-Antworten
- KI-Prompt-Erstellung: Ein passender Prompt wird in die Zwischenablage kopiert und kann in ChatGPT oder einem anderen KI-Dienst eingefügt werden

## Excel-Unterstützung installieren

CSV-Import und alle übrigen Funktionen benötigen keine zusätzlichen Python-Pakete. Für Excel-Dateien installiere optional `openpyxl`:

```bash
python -m pip install -r requirements-faq.txt
```

Windows:

```bat
py -m pip install -r requirements-faq.txt
```

## CSV-Format

Die erste Zeile muss Überschriften enthalten. Unterstützt werden deutsche und englische Namen. Kategorie ist optional.

```csv
Kategorie;Frage;Antwort
Versand;Wie lange dauert die Lieferung?;Die voraussichtliche Lieferzeit steht im Checkout.
Support;Wie erreiche ich euch?;Nutze bitte unser Kontaktformular.
```

## Antwortvorlagen und KI

Die integrierten Antwortvorlagen helfen, eigene Stichpunkte in einen passenden Ton zu bringen. Der KI-Prompt-Button erstellt einen kontextbezogenen Prompt aus Kategorie, Frage und Antwortentwurf. Es wird absichtlich kein KI-Anbieter automatisch kontaktiert und kein API-Schlüssel gespeichert: Zum tatsächlichen Formulieren den Prompt in einen KI-Dienst deiner Wahl kopieren und die Fakten und das Ergebnis vor der Veröffentlichung prüfen.

## Hinweise

- Die Anwendung startet mit drei Beispielen. Du kannst sie bearbeiten oder löschen.
- Projektdateien und Exporte werden erst dann angelegt, wenn du selbst einen Speicherort auswählst.
- HTML-Ausgaben sind eigenständige Dateien mit responsivem Layout und aufklappbaren Antworten.

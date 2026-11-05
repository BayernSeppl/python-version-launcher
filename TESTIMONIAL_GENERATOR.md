# Testimonial Studio

Ein lokaler, gut bedienbarer Testimonial-Generator für Windows, macOS und Linux. Das Tool hilft dabei, echte Kundenstimmen zu sammeln, zu kategorisieren, sauber aufzubereiten und als HTML, CSV, Markdown oder JSON zu exportieren.

## Starten

```bash
python testimonial_generator.py
```

Windows:

```bat
py testimonial_generator.py
```

## Funktionen

- Kundenstimmen erfassen, bearbeiten und löschen
- Bewertung mit 1–5 Sternen, Freigabestatus und Kategorie
- CSV-/Excel-Import für `Name;Unternehmen;Quote;Rating;Status;Kategorie;Quelle`
- Antwort- und Anfragevorlagen für den Aufbau einer professionellen Kundenbewertung
- Live-Vorschau
- Export als HTML, Markdown, CSV oder JSON
- Projekt local als JSON speichern und später wieder öffnen

## Excel-Unterstützung

Für XLSX-/XLSM-Dateien erforderlich:

```bash
python -m pip install -r requirements-testimonials.txt
```

## CSV-Format

Die erste Zeile der CSV kann Überschriften enthalten. Unterstützte Namen (optional deutsch oder englisch):

- Name: `Name`, `Kunde`, `Customer`
- Unternehmen: `Company`, `Unternehmen`, `Firma`
- Rolle: `Role`, `Rolle`, `Position`
- Kategorie: `Category`, `Kategorie`
- Status: `Status`, `Freigabe`
- Bewertung: `Rating`, `Bewertung`, `Stars`
- Quelle: `Source`, `Quelle`, `Channel`
- Zitat: `Quote`, `Zitat`, `Feedback`, `Review`, `Testimonial`

Beispiel:

```csv
Name;Unternehmen;Role;Category;Status;Rating;Source;Quote
Anna K.;Müller & Partner;Marketing-Leiterin;B2B;approved;5;Google;Das Produkt war schnell einsetzbar und sehr professionell.
```

## Hinweise

- Das Tool dient der Verwaltung echter Kundenstimmen und darf keine erfundenen Bewertungen erzeugen.
- Texte und Formulierungen müssen vor der Veröffentlichung human geprüft werden.
- Exporte und Projekte werden nur erstellt, wenn du einen Speicherort wählst.

# LottoPro Analyse

Eine Windows-Desktop-App für LOTTO 6 aus 49 mit einer lokalen SQLite-Datenbank, CSV-Import, Ordner-Aktualisierung mit Duplikaterkennung, Häufigkeitsgrafik, Vergleich der Gesamt- und jüngeren Häufigkeiten, letzter Auftritt/Pause sowie Tippfiltern und CSV-Export.

## Windows-EXE erstellen

1. Repository über **Code → Download ZIP** herunterladen und entpacken.
2. Python 3 installieren und beim Setup **Add Python to PATH** aktivieren. Tkinter/Tcl-Tk muss installiert sein.
3. Im Projektordner `build_lotto_exe.bat` doppelklicken.
4. Die EXE liegt danach unter `dist\LottoPro.exe`.

Beim ersten Build ist Internetzugang erforderlich, damit PyInstaller heruntergeladen werden kann. Die fertige EXE ist eine Windows-Anwendung und benötigt auf dem Ziel-PC keine separate Python-Installation.

## Historische Ziehungen importieren

Die App lädt keine Lotto-Webseiten im Hintergrund. Lade eine CSV-Datei aus einem offiziellen Lotterie-Archiv selbst herunter und wähle in der App **CSV importieren**. Für regelmäßige Aktualisierungen kannst du alle offiziellen CSV-Dateien in einen Ordner legen und **Ordner aktualisieren** wählen. Bereits gespeicherte Ziehungen werden erkannt und nicht doppelt hinzugefügt.

CSV-Zeilen müssen genau sechs verschiedene Hauptzahlen von 1 bis 49 enthalten, optional mit einem Datum, zum Beispiel:

```csv
Datum;Zahl1;Zahl2;Zahl3;Zahl4;Zahl5;Zahl6
03.01.2025;4;9;17;23;35;41
10.01.2025;2;8;13;28;34;47
```

Zeilen mit Zusatz-/Superzahlen oder zusätzlichen numerischen Spalten werden bewusst übersprungen; das Programm errät nicht, welche Spalten Hauptzahlen sind. Die CSV-Dateien müssen chronologisch sortiert sein (älteste Ziehung zuerst), damit die Pausenanzeige stimmt. Ziehungen ohne Datum werden importiert, können aber nicht chronologisch einsortiert werden.

Die SQLite-Datenbank liegt unter `%APPDATA%\LottoPro\lotto_data.sqlite3` und bleibt beim Ersetzen der EXE erhalten.

## Analyse-Hinweis

Häufigkeiten und Pausen beschreiben ausschließlich Vergangenes. Ein historischer Trend macht eine Zahl in einer fairen künftigen Ziehung nicht wahrscheinlicher; jede gültige Kombination hat dieselbe Chance. Bitte verantwortungsvoll spielen.

# LottoPro Analyse

Eine Windows-Desktop-App für Lotto 6 aus 49: übersichtliches Dashboard, Häufigkeitsgrafik, Häufigkeits-/Pausenwerte, CSV-Import, Tippfilter und CSV-Export.

## Windows-EXE erstellen

1. Repository über **Code → Download ZIP** herunterladen und entpacken (oder mit Git klonen).
2. Python 3 installieren. Im Installer **Add Python to PATH** aktivieren und sicherstellen, dass Tkinter/Tcl-Tk mitinstalliert wird.
3. Im entpackten Projektordner `build_lotto_exe.bat` doppelklicken.
4. Nach erfolgreichem Build liegt die Datei unter `dist\LottoPro.exe`; der Ordner wird geöffnet.

Beim ersten Build ist eine Internetverbindung erforderlich, damit PyInstaller installiert werden kann. Die fertige EXE ist für Windows erstellt und läuft ohne separate Python-Installation.

## CSV-Importformat

Eine CSV-Zeile muss genau sechs unterschiedliche Hauptzahlen von 1 bis 49 enthalten, zum Beispiel:

```csv
Datum;Zahl1;Zahl2;Zahl3;Zahl4;Zahl5;Zahl6
2025-01-04;3;12;18;27;33;46
2025-01-08;5;9;14;22;37;49
```

Kopfzeilen werden ignoriert. Für die Anzeige des Abstands zur letzten Ziehung müssen die Daten chronologisch sortiert sein (älteste Ziehung zuerst). Zusatz-/Superzahlen nicht in die sechs Hauptzahlen aufnehmen.

## Tipp-Generator

Der Zufallsmodus erstellt zufällige gültige Kombinationen, optional gefiltert nach Zahlensumme und Anzahl gerader Zahlen. „Häufige Zahlen berücksichtigen“ nutzt historische Häufigkeiten nur als Auswahlpräferenz. Das ist keine Vorhersage und verbessert nicht die mathematische Gewinnchance. Jede gültige Kombination hat bei einer fairen Ziehung dieselbe Wahrscheinlichkeit.

Demo-Daten sind synthetisch und ausdrücklich keine echten Ziehungsergebnisse. Die App verbindet sich nicht mit externen Diensten und lädt keine aktuellen Ziehungsdaten automatisch.

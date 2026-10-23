# Game Center

Live: https://franksander1967-ai.github.io/Games/

HTML-Spiele hinzufügen oder löschen und nach `main` pushen: GitHub Actions
erstellt die Kacheln in `index.html` neu und veröffentlicht GitHub Pages.
Auch HTML-Dateien in Unterordnern und `.htm` werden erkannt; die Startseite,
versteckte Ordner und Build-/Werkzeugordner sind ausgeschlossen.
Die vorhandenen Spiele werden vom Generator nur aufgelistet, nicht verändert.

Manuell: `python3 scripts/build_catalog.py`; prüfen mit
`python3 scripts/build_catalog.py --check` (keine Zusatzpakete nötig).
Layout und Suche werden in `index.html` außerhalb der GAMES-Markierungen bearbeitet.
Der Inhalt zwischen den Markierungen wird automatisch ersetzt.

Unter Settings → Pages muss die Quelle **GitHub Actions** ausgewählt sein.
Der Workflow lässt sich über Actions auch manuell starten. Er benötigt
Schreibrechte für Repository-Inhalte, um aktualisierte Kacheln zu speichern.

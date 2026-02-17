# ATK-Pro – Antenati Fliesen-Wiederhersteller
**Hinweis:** Dieses Projekt wird vollständig von einer einzigen Person entwickelt, gepflegt und unterstützt. Jedes Feedback, jede Meldung oder jeder Beitrag ist willkommen, aber es gibt kein Team oder keine Unternehmensstruktur hinter der Entwicklung.
## Beschreibung
ATK-Pro ist ein fortschrittliches Werkzeug für die Rekonstruktion, Archivierung und Abfrage von digitalisierten genealogischen Bildern und Dokumenten aus dem Portal Antenati. Das Projekt unterstützt die mehrsprachige Verwaltung und die Bereitstellung als eigenständige Anwendung für Windows.
## Hauptfunktionen
- Automatische Rekonstruktion von Bildern aus IIIF-Kacheln
- Mehrsprachige Unterstützung (20 Sprachen)
- Moderne grafische Benutzeroberfläche (Qt)
- EXE-Standalone und mehrsprachiger Installer
## Installation
1. Laden Sie den Installer ATK-Pro-Setup-v2.0.exe oder die Standalone-Executable ATK-Pro.exe aus dem Release-Bereich herunter.
1. Befolgen Sie die Anweisungen auf dem Bildschirm, um die Installation abzuschließen.
1. Starten Sie ATK-Pro über das Startmenü oder den Installationsordner.
## Projektstruktur
- `src/` – Hauptquellcode (GUI, Logik, Module)
- `assets/` – Mehrsprachige Assets (Anleitungen, Vorlagen, Ressourcen)
- `locales/` – .ini-Übersetzungsdateien für jede Sprache
- `docs_generali/` – Glossare, allgemeine Dokumentation, Roadmap
- `scripts/` – Wartungsskripte, Übersetzung, Validierung
- `tests/` – Automatisierte und Abdeckungstests
- `dist/` – Ausgabe Build/Installer
## Dokumentation
- Die historische und vertiefende Dokumentation ist nun unter `docs_generali/archivio/` archiviert.
- Die vorliegende README und die Datei `CHANGELOG.md` fassen den Status und die wichtigsten Meilensteine des Projekts zusammen.
## Geschichte und Entwicklung
Das Projekt entstand als Weiterentwicklung von Werkzeugen für die digitale Genealogie, mit Fokus auf Transparenz, historische Archivierung und internationale Unterstützung. Jeder Meilenstein wird im Repository verfolgt und dokumentiert.
## Credits
Entwicklung und Wartung: Daniele Pigoli
Beiträge: siehe Changelog und Release Notes
## Änderungsprotokoll
Lesen Sie die Datei `docs_generali/CHANGELOG.md` für die wichtigsten Neuigkeiten und Meilensteine des Projekts.
Für historische Details und vollständige Notizen siehe den Ordner `docs_generali/archivio/`.

-----
## Aktueller Status
- Alle aktiven Module wurden mit direkter und defensiver Abdeckung getestet
- Annotation mit Block `# === Testabdeckung ===` in validierten Modulen
- Das Modul main.py wurde, obwohl es nur teilweise abgedeckt ist (64%), logisch validiert, da es als orchestrativ fungiert.
### Nächste Schritte
- Vorbereitung der v2.1 mit inkrementeller Weiterentwicklung und aktualisierter Dokumentation

✍️ Herausgegeben von Daniele Pigoli – mit der Absicht, technische Strenge und historisches Gedächtnis zu vereinen.

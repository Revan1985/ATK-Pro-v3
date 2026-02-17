# ATK-Pro – Reconstruitor de plăci ancestrale
**Notă:** Acest proiect este dezvoltat, întreținut și susținut în întregime de o singură persoană. Orice feedback, raportare sau contribuție este binevenită, dar nu există o echipă sau o structură corporativă în spatele dezvoltării.
## Descriere
ATK-Pro este un instrument avansat pentru reconstrucția, arhivarea și consultarea imaginilor și documentelor genealogice digitalizate de pe portalul Antenati. Proiectul suportă gestionarea multilingvă și distribuția ca aplicație independentă pentru Windows.
## Funcționalități principale
- Reconstrucție automată a imaginilor din dale IIIF
- Suport multilingv (20 de limbi)
- Interfață grafică modernă (Qt)
- Construiți EXE autonom și instalator multilingv
## Instalare
1. Descărcați fișierul de instalare ATK-Pro-Setup-v2.0.exe sau executabilul independent ATK-Pro.exe din secțiunea de lansări.
1. Urmați instrucțiunile de pe ecran pentru a finaliza instalarea.
1. Porniți ATK-Pro din meniul Start sau din folderul de instalare.
## Structura proiectului
- `src/` – Cod sursă principal (GUI, logică, module)
- `resurse/` – Resurse multilingve (ghiduri, șabloane, resurse)
- `locales/` – Fișiere de traducere .ini pentru fiecare limbă
- `docs_generali/` – Glosare, documentație generală, foaie de parcurs
- `scripturi/` – Scripturi de întreținere, traducere, validare
- `teste/` – Teste automate și de acoperire
- `dist/` – Build/installer de ieșire
## Documentație
- Documentația istorică și de aprofundare este acum arhiva în `docs_generali/archivio/`.
- Prezentul README și fișierul `CHANGELOG.md` rezumă stadiul și etapele principale ale proiectului.
## Istorie și dezvoltare
Proiectul ia naștere ca o evoluție a instrumentelor pentru genealogia digitală, cu accent pe transparență, arhivare istorică și suport internațional. Fiecare etapă este urmărită și documentată în depozit.
## Credite
Dezvoltare și întreținere: Daniele Pigoli
Contribuții: vezi changelog și note de lansare
## Jurnal de modificări
Consultați fișierul `docs_generali/CHANGELOG.md` pentru cele mai importante noutăți și etape ale proiectului.
Pentru detalii istorice și note complete, vezi dosarul `docs_generali/archivio/`.

-----
## Stare actuală
- Toate modulele active au fost testate cu acoperire directă și defensivă
- Adnotare cu blocul `# === Acoperire test ===` în modulele validate
- Modulul main.py, chiar și cu o acoperire parțială (64%), a fost validat logic, fiind orchestrațional
### Pașii următori
- Pregătirea versiunii 2.1 cu evoluție incrementală și documentație actualizată

✍️ Îngrijit de Daniele Pigoli – cu intenția de a uni rigoarea tehnică și memoria istorică.

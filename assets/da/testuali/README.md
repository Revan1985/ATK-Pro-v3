# ATK-Pro – Antenati Flisegenopbygger
**Bemærk:** Dette projekt er udviklet, vedligeholdt og understøttet udelukkende af én person. Enhver feedback, indberetning eller bidrag er velkommen, men der er intet team eller nogen virksomhedsstruktur bag udviklingen.
## Beskrivelse
ATK-Pro er et avanceret værktøj til rekonstruktion, arkivering og konsultation af digitaliserede genealogiske billeder og dokumenter fra Antenati-portalen. Projektet understøtter flersproget administration og distribution som en selvstændig applikation til Windows.
## Hovedfunktioner
- Automatisk rekonstruktion af billeder fra IIIF-fliser
- Flersproget support (20 sprog)
- Moderne grafisk brugerflade (Qt)
- Byg EXE standalone og flersproget installationsprogram
## Installation
1. Download ATK-Pro-Setup-v2.0.exe-installeren eller den selvstændige eksekverbare fil ATK-Pro.exe fra udgivelsessektionen.
1. Følg instruktionerne på skærmen for at fuldføre installationen.
1. Start ATK-Pro fra Start-menuen eller fra installationsmappen.
## Projektstruktur
- `src/` – Hovedkildekode (GUI, logik, moduler)
- `assets/` – Flersprogede aktiver (guides, skabeloner, ressourcer)
- `locales/` – .ini oversættelsesfiler for hvert sprog
- `docs_generali/` – Ordliste, generel dokumentation, køreplan
- `scripts/` – Vedligeholdelses-, oversættelses- og valideringscripts
- `tests/` – Automatiserede og dækkende tests
- `dist/` – Output build/installationsprogram
## Dokumentation
- Den historiske og uddybende dokumentation er nu arkiveret i `docs_generali/archivio/`.
- Denne README og filen `CHANGELOG.md` opsummerer projektets status og vigtigste milepæle.
## Historie og udvikling
Projektet opstod som en videreudvikling af værktøjer til digital genealogi med fokus på gennemsigtighed, historisk arkivering og international support. Hver milepæl spores og dokumenteres i lageret.
## Kreditter
Udvikling og vedligeholdelse: Daniele Pigoli
Bidrag: se changelog og udgivelsesnoter
## Log over ændringer
Se filen `docs_generali/CHANGELOG.md` for de vigtigste nyheder og milepæle i projektet.
For historiske detaljer og fuldstændige noter, se mappen `docs_generali/archivio/`.

-----
## Nuværende status
- Alle aktive moduler er blevet testet med direkte og defensiv dækning
- Annotation med blok `# === Testdækning ===` i validerede moduler
- Modulet main.py, selv med delvis dækning (64%), er logisk valideret, da det er orkestrerende
### Næste skridt
- Forbered v2.1 med inkrementel udvikling og opdateret dokumentation

✍️ Redigeret af Daniele Pigoli – med det formål at forene teknisk stringens og historisk hukommelse.

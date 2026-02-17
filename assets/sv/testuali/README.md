# ATK-Pro – Antenati Tile Rebuilder
**Notera:** Detta projekt utvecklas, underhålls och stöds helt av en enda person. All feedback, rapportering eller bidrag är välkomna, men det finns inget team eller företagsstruktur bakom utvecklingen.
## Beskrivning
ATK-Pro är ett avancerat verktyg för rekonstruktion, lagring och konsultation av digitaliserade genealogiska bilder och dokument från portalen Antenati. Projektet stöder flerspråkig hantering och distribution som en fristående applikation för Windows.
## Huvudfunktioner
- Automatisk rekonstruktion av bilder från IIIF-brickor
- Flerspråkigt stöd (20 språk)
- Modernt grafiskt gränssnitt (Qt)
- Bygg fristående EXE och flerspråkig installationsprogram
## Installation
1. Ladda ner ATK-Pro-Setup-v2.0.exe-installationsprogrammet eller den fristående körbara filen ATK-Pro.exe från releasesektionen.
1. Följ instruktionerna på skärmen för att slutföra installationen.
1. Starta ATK-Pro från Start-menyn eller från installationsmappen.
## Projektstruktur
- `src/` – Huvudsaklig källkod (GUI, logik, moduler)
- `tillgångar/` – Flerspråkiga tillgångar (guider, mallar, resurser)
- `locales/` – .ini-översättningsfiler för varje språk
- `docs_generali/` – Ordlistor, allmän dokumentation, färdplan
- `scripts/` – Skript för underhåll, översättning, validering
- `tester/` – Automatiska tester och täckning
- `dist/` – Utdata för byggnation/installationsprogram
## Dokumentation
- Den historiska och fördjupade dokumentationen arkiveras nu i `docs_generali/archivio/`.
- Denna README och filen `CHANGELOG.md` sammanfattar projektets status och milstolpar.
## Historia och utveckling
Projektet föddes som en vidareutveckling av verktyg för digital genealogi, med fokus på transparens, historiskt arkiv och internationellt stöd. Varje milstolpe spåras och dokumenteras i förrådet.
## Krediter
Utveckling och underhåll: Daniele Pigoli
Bidrag: se ändringslogg och versionsanteckningar
## Ändringslogg
Se till filen `docs_generali/CHANGELOG.md` för de viktigaste nyheterna och milstolparna i projektet.
För historiska detaljer och fullständiga anteckningar, se mappen `docs_generali/archivio/`.

-----
## Nuvarande status
- Alla aktiva moduler har testats med direkt och defensiv täckning
- Anteckning med block `# === Testtäckning ===` i validerade moduler
- Modulen main.py, trots delvis täckning (64%), har logiskt validerats eftersom den är orkestrerande
### Nästa steg
- Förbered v2.1 med inkrementell utveckling och uppdaterad dokumentation

✍️ Redigerad av Daniele Pigoli – med avsikten att förena teknisk stringens och historiskt minne.

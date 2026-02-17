# ATK-Pro – Antenati Tile Rebuilder
**Merk:** Dette prosjektet er utviklet, vedlikeholdt og støttet utelukkende av én enkelt person. Alle tilbakemeldinger, rapporter eller bidrag er velkomne, men det er ikke noe team eller noen bedriftsstruktur bak utviklingen.
## Beskrivelse
ATK-Pro er et avansert verktøy for rekonstruksjon, lagring og konsultasjon av digitaliserte genealogiske bilder og dokumenter fra Antenati-portalen. Prosjektet støtter flerspråklig administrasjon og distribusjon som en frittstående applikasjon for Windows.
## Hovedfunksjoner
- Automatisk rekonstruksjon av bilder fra IIIF-fliser
- Flerspråklig støtte (20 språk)
- Moderne grafisk grensesnitt (Qt)
- Bygg frittstående EXE og flerspråklig installasjonsprogram
## Installasjon
1. Last ned ATK-Pro-Setup-v2.0.exe-installasjonsprogrammet eller den frittstående kjørbare filen ATK-Pro.exe fra utgivelsesseksjonen.
1. Følg instruksjonene på skjermen for å fullføre installasjonen.
1. Start ATK-Pro fra Start-menyen eller fra installasjonsmappen.
## Prosjektstruktur
- `src/` – Hovedkildekode (GUI, logikk, moduler)
- `assets/` – Flerspråklige ressurser (guider, maler, ressurser)
- `lokaler/` – .ini-oversettelsesfiler for hvert språk
- `docs_generali/` – Ordliste, generell dokumentasjon, veikart
- `scripts/` – Vedlikeholds-, oversettelses- og valideringsskript
- `tester/` – Automatiske tester og dekning
- `dist/` – Utdata bygg/installasjonsprogram
## Dokumentasjon
- Den historiske og dyptgående dokumentasjonen er nå arkivert i `docs_generali/archivio/`.
- Denne README-filen og filen `CHANGELOG.md` oppsummerer prosjektets status og hovedmilepæler.
## Historie og utvikling
Prosjektet oppsto som en videreutvikling av verktøy for digital genealogi, med fokus på åpenhet, historisk arkivering og internasjonal støtte. Hver milepæl spores og dokumenteres i arkivet.
## Kreditter
Utvikling og vedlikehold: Daniele Pigoli
Bidrag: se endringslogg og utgivelsesnotater
## Endringslogg
Se filen `docs_generali/CHANGELOG.md` for de viktigste nyhetene og milepælene i prosjektet.
For historiske detaljer og fullstendige notater, se mappen `docs_generali/archivio/`.

-----
## Nåværende status
- Alle aktive moduler er testet med direkte og defensiv dekning
- Annotasjon med blokk `# === Testdekning ===` i validerte moduler
- Modulen main.py, til tross for delvis dekning (64%), ble logisk validert da den er orkestrerende
### Neste steg
- Forberede v2.1 med inkrementell utvikling og oppdatert dokumentasjon

✍️ Kuratert av Daniele Pigoli – med intensjon om å forene teknisk stringens og historisk hukommelse.

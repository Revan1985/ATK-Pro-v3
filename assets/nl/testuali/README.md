# ATK-Pro – Antenati Tegel Herbouwer
**Opmerking:** Dit project wordt volledig ontwikkeld, onderhouden en ondersteund door één persoon. Elke feedback, melding of bijdrage is welkom, maar er is geen team of bedrijfsstructuur achter de ontwikkeling.
## Beschrijving
ATK-Pro is een geavanceerd hulpmiddel voor de reconstructie, opslag en raadpleging van gedigitaliseerde genealogische afbeeldingen en documenten van het portaal Antenati. Het project ondersteunt meertalig beheer en distributie als een standalone applicatie voor Windows.
## Belangrijkste functionaliteiten
- Automatische reconstructie van afbeeldingen uit IIIF-tegels
- Meertalige ondersteuning (20 talen)
- Moderne grafische interface (Qt)
- Maak EXE standalone en meertalige installer
## Installatie
1. Download de ATK-Pro-Setup-v2.0.exe installer of het standalone uitvoerbare bestand ATK-Pro.exe uit de release sectie.
1. Volg de instructies op het scherm om de installatie te voltooien.
1. Start ATK-Pro vanuit het Startmenu of de installatiemap.
## Projectstructuur
- `src/` – Hoofdbroncode (GUI, logica, modules)
- `assets/` – Meertalige assets (handleidingen, sjablonen, bronnen)
- `locales/` – .ini vertaalbestanden voor elke taal
- `docs_generali/` – Glossaria, algemene documentatie, roadmap
- `scripts/` – Onderhouds-, vertaal- en validatiescripts
- `tests/` – Automatische en dekkingscontroles
- `dist/` – Output build/installer
## Documentatie
- De historische en verdiepende documentatie is nu gearchiveerd in `docs_generali/archivio/`.
- Dit README en het bestand `CHANGELOG.md` vatten de status en de belangrijkste mijlpalen van het project samen.
## Geschiedenis en ontwikkeling
Het project is ontstaan als evolutie van tools voor digitale genealogie, met aandacht voor transparantie, historische archivering en internationale ondersteuning. Elke mijlpaal wordt bijgehouden en gedocumenteerd in de repository.
## Credits
Ontwikkeling en onderhoud: Daniele Pigoli
Bijdragen: zie changelog en release notes
## Wijzigingslogboek
Bekijk het bestand `docs_generali/CHANGELOG.md` voor de belangrijkste nieuwigheden en projectmijlpalen.
Voor historische details en volledige notities, zie de map `docs_generali/archivio/`.

-----
## Huidige status
- Alle actieve modules zijn getest met directe en defensieve dekking
- Annotatie met blok `# === Testdekking ===` in gevalideerde modules
- Het main.py-module, ondanks gedeeltelijke dekking (64%), is logisch gevalideerd omdat het orchestratief is
### Volgende stappen
- Bereid v2.1 voor met incrementele evolutie en bijgewerkte documentatie

✍️ Samengesteld door Daniele Pigoli – met de bedoeling om technische nauwkeurigheid en historische herinnering te verenigen.

# ATK-Pro – Antenati Tile Rebuilder

**Nota:** Questo progetto è sviluppato, mantenuto e supportato interamente da una sola persona. Ogni feedback, segnalazione o contributo è benvenuto, ma non esiste un team o una struttura aziendale dietro lo sviluppo.

## Descrizione
ATK-Pro è uno strumento avanzato per la ricostruzione, archiviazione e consultazione di immagini e documenti genealogici digitalizzati dal portale Antenati. Il progetto supporta la gestione multilingua e la distribuzione come applicazione standalone per Windows.

## Funzionalità principali
- Ricostruzione automatica di immagini da tile IIIF
- Supporto multilingua (20 lingue)
- Interfaccia grafica moderna (Qt)
- Build EXE standalone e installer multilingua


## Installazione
1. Scarica l’installer ATK-Pro-Setup-v2.0.exe oppure l’eseguibile standalone ATK-Pro.exe dalla sezione release.
2. Segui le istruzioni a schermo per completare l’installazione.
3. Avvia ATK-Pro dal menu Start o dalla cartella di installazione.

## Struttura del progetto
- `src/` – Codice sorgente principale (GUI, logica, moduli)
- `assets/` – Asset multilingua (guide, template, risorse)
- `locales/` – File di traduzione .ini per ogni lingua
- `docs_generali/` – Glossari, documentazione generale, roadmap
- `scripts/` – Script di manutenzione, traduzione, validazione
- `tests/` – Test automatici e di copertura
- `dist/` – Output build/installer

## Documentazione
- La documentazione storica e di approfondimento è ora archiviata in `docs_generali/archivio/`.
- Il presente README e il file `CHANGELOG.md` riassumono lo stato e le tappe principali del progetto.

## Storia e sviluppo
Il progetto nasce come evoluzione di tool per la genealogia digitale, con attenzione a trasparenza, archiviazione storica e supporto internazionale. Ogni milestone è tracciata e documentata nel repository.

## Credits
Sviluppo e manutenzione: Daniele Pigoli  
Contributi: vedi changelog e note di rilascio


## Changelog
Consulta il file `docs_generali/CHANGELOG.md` per le principali novità e tappe del progetto.
Per dettagli storici e note complete, vedi la cartella `docs_generali/archivio/`.

---


## Stato attuale
- Tutti i moduli attivi sono stati testati con copertura diretta e difensiva
- Annotazione con blocco `# === Copertura test ===` nei moduli validati
- Il modulo main.py, pur con copertura parziale (64%), è stato validato logicamente in quanto orchestrativo

### Prossimi passi
- Preparare la v2.1 con evoluzione incrementale e documentazione aggiornata

✍️ Curato da Daniele Pigoli – con l’intento di unire rigore tecnico e memoria storica.
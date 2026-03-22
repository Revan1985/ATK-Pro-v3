# CHANGELOG – ATK-Pro

## v2.2.0 (22 March 2026 / 22 marzo 2026)

### English
#### New Features
- **PDF as output format**: PDF export is now available as a dedicated output format in the format selection dialog.
  Users can select PDF alone or alongside PNG/JPG/TIFF to generate a complete multi-page PDF of all pages in a register or document.
- **Automatic PDF generation**: PDF is generated fully automatically from the reconstructed IIIF images — no external tools or intermediate steps required.

#### Improvements
- Localized PDF label and placeholder texts in all 20 supported languages.
- PDF checkbox added to Step 1 of the user guide in all 20 languages.
- Updated PDF section in all guides: replaces obsolete popup window description with the new automatic generation workflow.
- Removed version number from footer of all textual files (guides, disclaimer, author page, project page) — version displayed only in installer/app header.
- Removed obsolete `window3.webp` screenshots from all 20 language assets.
- Updated installer version reference to `vx.x.x` (version-agnostic) in all guides.

#### Build Notes (macOS)
- macOS build is not signed with an Apple Developer certificate.
  If macOS shows an "App is damaged" or "unidentified developer" warning, use one of these methods:
  1. Run in Terminal: `xattr -cr /Applications/ATK-Pro.app`
  2. Control+click the app icon → Open → Open
  3. System Settings → Privacy & Security → "Open Anyway"

#### Bug Fixes
- Fixed missing PDF suffix removal from output filename.
- Fixed leftover `_pdftmp.png` temporary files when using TIFF+PDF format.
- Fixed localized output folder memory across sessions.
- Fixed numeric ordering of canvas pages in PDF output.
- Fixed localized placeholder for failed canvas downloads.

### Italiano
#### Nuove funzionalità
- **PDF come formato di output**: l'esportazione PDF è ora disponibile come formato dedicato nel dialogo di scelta dei formati.
  È possibile selezionare PDF da solo o insieme a PNG/JPG/TIFF per generare un PDF multipagina completo di tutte le pagine di un registro o documento.
- **Generazione PDF automatica**: il PDF viene generato in modo completamente automatico a partire dalle immagini IIIF ricostruite — senza strumenti esterni né passaggi intermedi.

#### Miglioramenti
- Etichetta PDF e testi placeholder localizzati in tutte le 20 lingue supportate.
- Checkbox PDF aggiunta allo Step 1 della guida utente in tutte le 20 lingue.
- Sezione PDF aggiornata in tutte le guide: sostituisce la descrizione della vecchia finestra popup con il nuovo flusso di generazione automatica.
- Rimosso il numero di versione dal footer di tutti i file testuali (guida, disclaimer, pagina autore, pagina progetto) — la versione appare solo nell'intestazione dell'installer/app.
- Rimossi gli screenshot `window3.webp` obsoleti da tutti gli asset delle 20 lingue.
- Riferimento all'installer aggiornato a `vx.x.x` (indipendente dalla versione) in tutte le guide.

#### Note build (macOS)
- La build per macOS non è firmata con un certificato Apple Developer.
  Se macOS mostra un avviso "app danneggiata" o "sviluppatore non identificato", usare uno di questi metodi:
  1. Eseguire nel Terminale: `xattr -cr /Applications/ATK-Pro.app`
  2. Clic con Control sull'icona dell'app → Apri → Apri
  3. Impostazioni di Sistema → Privacy e sicurezza → "Apri comunque"

#### Correzioni di bug
- Corretto mancato rimosso del suffisso `_registro_completo` dal nome del file PDF in output.
- Corretti file temporanei `_pdftmp.png` residui nell'output con formato TIFF+PDF.
- Corretta la memorizzazione della cartella di output tra una sessione e l'altra.
- Corretto l'ordine numerico delle pagine canvas nel PDF.
- Corretto il placeholder localizzato per canvas non scaricabili.

## v2.0 (2026)
- Public release version 2.0: IIIF tile image reconstruction, multilingual support, Qt interface, EXE build and installer
- Batch optimization, error handling, advanced logging, full automation
- Documentation update and rationalization
## v1.x (2023-2025)
- Experimental versions and prototypes
- Progressive improvements to workflow, compatibility, data export
-----
For historical details and complete notes, consult the docs_generali/archive folder.

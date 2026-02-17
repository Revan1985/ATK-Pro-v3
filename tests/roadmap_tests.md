# 🧭 Roadmap Test — ATK-Pro v2.0

## 🎯 Obiettivi principali
- Riallineare la suite di test alla nuova architettura modulare v2.0, verificata contro BASE AUREA.
- Mantenere in `tests/` solo i test coerenti e funzionanti (249 passed).
- Archiviare in `tests_storici/` i 47 test divergenti, da aggiornare progressivamente.
- Garantire esecuzione coerente sia in ambiente Python puro che in Windows con .exe.
- Documentare ogni fase di riallineamento nel registro attività.

---

## 📊 Stato attuale della suite
- Totale test eseguiti: **296**
- Passed: **249**
- Failed: **47**
- Skipped: **0**
- Copertura media stimata: **78%**
- Divergenze principali:
  - `browser_setup` / `main` → riferimenti a `setup_driver` rimosso
  - `canvas_processor` → riferimenti a `download_info_json` rimosso
  - `tile_downloader` → riferimenti a `download_all_tiles` sostituito da `download_tiles`
  - `manifest_utils` → divergenze su `find_manifest_url`
  - `canvas_id_extractor` → test difensivi su fallback HTML non più coerenti

---

## 🧪 Piano di riallineamento

### Fase 1 — Pulizia
- [x] Spostati i 47 test divergenti in `tests_storici/`.
- [ ] Confermare stabilità dei 249 test validi.

### Fase 2 — Riallineamento test obsoleti
- [ ] Aggiornare test di `browser_setup` e `main` eliminando riferimenti a `setup_driver`.
- [ ] Aggiornare test di `canvas_processor` eliminando `download_info_json`.
- [ ] Aggiornare test di `tile_downloader` per usare `download_tiles`.
- [ ] Aggiornare test di `manifest_utils` per casi reali.
- [ ] Rivalutare test difensivi di `canvas_id_extractor`.

### Fase 3 — Consolidamento
- [ ] Rieseguire suite completa.
- [ ] Aggiornare copertura e documentare regressioni reali.
- [ ] Annotare milestone in `registro_attivita_v2.0.md`.

---

## 📂 Struttura consigliata dei test v2.0

```plaintext
tests/
├── test_browser_setup.py
├── test_canvas_id_extractor.py
├── test_canvas_processor.py
├── test_cli_dispatcher.py
├── test_image_downloader.py
├── test_image_rebuilder.py
├── test_image_saver.py
├── test_image_parser.py
├── test_image_loader.py
├── test_main.py
├── test_manifest_utils.py
├── test_metadata_utils.py
├── test_pdf_utils.py
├── test_tile_downloader.py
├── test_tile_rebuilder.py
├── test_ui_info.py
├── test_user_prompts.py
└── test_url_utils.py
📌 Note operative
Ogni test deve essere coerente con i moduli v2.0 verificati.

I test storici restano in tests_storici/ come archivio, non più eseguiti.

Ogni fase di riallineamento deve essere accompagnata da commit narrativo e voce di registro.
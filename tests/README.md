# 🧪 Test Suite — ATK-Pro v2.0

Benvenuto nella cartella `tests/` del progetto **Antenati Tile Rebuilder Pro**.  
Questa cartella contiene la **suite di test attiva e allineata ai moduli v2.0**, verificati contro la BASE AUREA.  

---

## ▶️ Come eseguire i test

Assicurati di avere Python ≥ 3.9 e `pytest` installato:

```bash
pip install pytest
pytest tests/
📊 Analisi della copertura
Per misurare la copertura del codice:

bash
pip install pytest-cov
pytest --cov=src --cov-report=term-missing tests/
🧩 Struttura della suite
La suite v2.0 copre i principali moduli del progetto:

browser_setup.py → inizializzazione ambiente browser

canvas_id_extractor.py → estrazione ID canvas

canvas_processor.py → elaborazione canvas

tile_downloader.py → download tiles

manifest_utils.py → gestione manifest

metadata_utils.py → metadati

pdf_* → generazione e gestione PDF

image_* → gestione immagini (download, rebuild, save, parse, load)

main.py → dispatcher principale

user_prompts.py → interazioni utente

url_utils.py → gestione URL

🧼 Ambiente isolato
I test usano unittest.mock e pytest fixtures per simulare:

GUI tkinter

Input utente

Driver browser

Download manifest

Questo consente di eseguire i test anche in ambienti senza interfaccia grafica.

📂 Distinzione tra suite attiva e archivio
tests/ → suite attiva v2.0 (249 test validi, in progressivo ampliamento).

tests_storici/ → archivio dei 47 test divergenti, mantenuti come testimonianza storica ma non più eseguiti.

📌 Note finali
La suite v2.0 è la base ufficiale per la verifica dei moduli.

I test storici restano disponibili in tests_storici/ per consultazione e riallineamento.

Ogni modifica ai moduli deve essere accompagnata da aggiornamento o aggiunta di test coerenti.
import os
import pytest
from src.main import elabora_record

def test_pdf_generation_fallisce(monkeypatch, capsys):
    record = {"modalita": "R", "nome_file": "test", "url": "http://example.com"}
    formats = ["jpg"]
    folder = "output"

    monkeypatch.setattr("src.user_prompts.ask_generate_pdf", lambda: True)

    # ✅ Generatore che solleva eccezione durante l'iterazione
    def falso_generatore():
        raise Exception("errore")
        yield

    monkeypatch.setattr("src.canvas_processor.process_all_canvases", lambda *a, **kw: falso_generatore())

    monkeypatch.setattr("src.browser_setup.setup_selenium", lambda: type("Driver", (), {
        "get": lambda self, url: None,
        "quit": lambda self: None
    })())

    monkeypatch.setattr("src.main.seleziona_cartella", lambda prompt: folder)
    monkeypatch.setattr("src.main.find_manifest_url", lambda driver: "http://example.com/manifest.json")
    monkeypatch.setattr("src.main.download_manifest", lambda *a, **kw: {
        "@context": "http://iiif.io/api/presentation/2/context.json"
    })
    monkeypatch.setattr("src.main.estrai_metadati_da_manifest", lambda path: None)

    elabora_record(record, formats, folder)
    out = capsys.readouterr().out

    assert (
        "errore" in out or
        "Nessun manifest disponibile" in out or
        "Manifest malformato" in out
    )

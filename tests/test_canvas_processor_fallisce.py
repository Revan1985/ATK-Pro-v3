import pytest
from src.canvas_processor import process_all_canvases

def test_process_all_canvases_manifest_malformato(capsys):
    manifest = {"sequences": None}  # simulazione manifest malformato
    output_folder = "output"
    formats = ["jpg"]

    try:
        result = process_all_canvases(
            manifest=manifest,
            output_folder=output_folder,
            formats=formats,
            base_filename_prefix="test",
            manifest_path="manifest.json",
            generate_pdf=False,
            page_url="http://example.com"
        )
        for _ in result:
            pass
    except Exception:
        pass

    out = capsys.readouterr().out
    assert "Manifest malformato" in out or "errore" in out

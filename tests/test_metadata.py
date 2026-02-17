import json
import pytest
from src.tile_rebuilder import build_image_metadata

def test_metadata_minima():
    meta = build_image_metadata()
    # Deve contenere almeno il campo Software e ATK-Pro-Version
    assert meta["Software"].startswith("Antenati")
    assert "ATK-Pro-Version" in meta

def test_metadata_completa(tmp_path):
    meta = build_image_metadata(
        ua="UserAgentX",
        ark="ark:/123",
        canvas_id="canvas42",
        page_label="p.10",
        range_label="1-5",
        description="descrizione",
        source_url="http://esempio",
        atk_version="1.5-test"
    )
    # Verifica presenza di tutti i campi
    for key in ["UA","ARK","CanvasID","Page","Range","Description","Source"]:
        assert key in meta
    # Il sidecar JSON è valido
    parsed = json.loads(meta["_json"])
    assert parsed["UA"] == "UserAgentX"
    assert parsed["ATK-Pro-Version"] == "1.5-test"

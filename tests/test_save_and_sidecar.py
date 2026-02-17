import os
from PIL import Image
import pytest
from src.tile_rebuilder import TileRebuilder, build_image_metadata

def test_embed_and_save(tmp_path, sample_tiles):
    out_img = tmp_path / "out.png"
    meta = build_image_metadata(description="dsc")
    tr = TileRebuilder(sample_tiles, str(out_img), (2,2), (10,10), metadata=meta)
    tr.save()

    # Il file immagine e il .json sidecar esistono
    assert out_img.exists()
    sidecar = tmp_path / "out.json"
    assert sidecar.exists()
    # Contenuto JSON corrisponde al meta["_json"]
    content = sidecar.read_text(encoding="utf-8")
    assert '"Description": "dsc"' in content

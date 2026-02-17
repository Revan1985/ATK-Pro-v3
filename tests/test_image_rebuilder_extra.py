# tests/test_image_rebuilder_extra.py
import io
import os
from PIL import Image
import pytest
import src.image_rebuilder as ir

def make_dummy_jpg(path):
    img = Image.new("RGB", (10, 10), (255, 0, 0))
    img.save(path)

def test_tile_mancante(tmp_path, capsys):
    info = {"width": 10, "height": 10, "tiles": [{"width": 10}]}
    # Nessun tile creato → mancante
    result = ir.rebuild_image(info, tmp_path)
    out = capsys.readouterr().out
    assert "Tile mancante" in out
    assert isinstance(result, Image.Image)

def test_tile_corrotto(tmp_path, capsys):
    info = {"width": 10, "height": 10, "tiles": [{"width": 10}]}
    bad_tile = tmp_path / "tile_0_0.jpg"
    bad_tile.write_text("non è un'immagine valida")
    result = ir.rebuild_image(info, tmp_path)
    out = capsys.readouterr().out
    assert "Errore con il tile" in out
    assert isinstance(result, Image.Image)

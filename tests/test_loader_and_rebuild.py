import os
from PIL import Image
import pytest
from src.tile_rebuilder import TileRebuilder

@pytest.fixture
def sample_tiles(tmp_path):
    folder = tmp_path / "tiles"
    folder.mkdir()
    # Crea 4 immagini colorate 10×10
    colors = ["red","green","blue","yellow"]
    for i, color in enumerate(colors):
        img = Image.new("RGB", (10,10), color)
        img.save(folder / f"tile_{i}.png")
    return str(folder)

def test_load_tiles_count(sample_tiles):
    tr = TileRebuilder(sample_tiles, "out.png", (2,2), (10,10))
    tiles = tr.load_tiles()
    assert len(tiles) == 4

def test_rebuild_canvas_dimensions(sample_tiles):
    tr = TileRebuilder(sample_tiles, "out.png", (2,2), (10,10), padding=(1,2))
    canvas = tr.rebuild()
    # width = 2*10 + 1*1, height = 2*10 + 1*2
    assert canvas.size == (21,22)

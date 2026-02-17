import os
import json
import pytest
from PIL import Image
import src.tile_rebuilder as tr


def create_dummy_tiles(tmp_path, cols=2, rows=2, size=(10, 10)):
    """Crea una griglia di tile dummy RGB in tmp_path."""
    for r in range(rows):
        for c in range(cols):
            img = Image.new("RGB", size, color=(r*50, c*50, 100))
            img.save(tmp_path / f"tile_{r}_{c}.jpg")


def test_rebuild_creates_correct_size(tmp_path):
    create_dummy_tiles(tmp_path, cols=2, rows=2, size=(10, 10))
    rebuilder = tr.TileRebuilder(
        input_dir=str(tmp_path),
        output_path=str(tmp_path / "out.png"),
        grid_size=(2, 2),
        tile_size=(10, 10),
    )
    canvas = rebuilder.rebuild()
    assert canvas.size == (20, 20)  # 2x2 tile da 10px


def test_save_creates_image_and_json(tmp_path):
    create_dummy_tiles(tmp_path, cols=1, rows=1, size=(8, 8))
    metadata = tr.build_image_metadata(
        ua="tester", description="dummy image", canvas_id="c1"
    )
    rebuilder = tr.TileRebuilder(
        input_dir=str(tmp_path),
        output_path=str(tmp_path / "out.png"),
        grid_size=(1, 1),
        tile_size=(8, 8),
        metadata=metadata,
    )
    rebuilder.save()

    out_img = tmp_path / "out.png"
    out_json = tmp_path / "out.json"
    assert out_img.exists()
    assert out_json.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["UA"] == "tester"
    assert data["Description"] == "dummy image"


def test_rebuild_with_missing_tiles_warns(tmp_path, caplog):
    # Creo solo 1 tile invece di 4
    create_dummy_tiles(tmp_path, cols=1, rows=1, size=(5, 5))
    rebuilder = tr.TileRebuilder(
        input_dir=str(tmp_path),
        output_path=str(tmp_path / "out.png"),
        grid_size=(2, 2),
        tile_size=(5, 5),
    )
    with caplog.at_level("WARNING"):
        canvas = rebuilder.rebuild()
    assert "Numero di tile" in caplog.text
    assert isinstance(canvas, Image.Image)

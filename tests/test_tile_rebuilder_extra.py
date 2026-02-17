# tests/test_tile_rebuilder_extra.py
import json
from pathlib import Path
import pytest
from PIL import Image
import src.tile_rebuilder as tr


def make_dummy_image(path, size=(10, 10), color=(255, 0, 0)):
    img = Image.new("RGB", size, color)
    img.save(path)


# --- build_image_metadata ---
def test_build_image_metadata_all_fields():
    meta = tr.build_image_metadata(
        ua="UA", ark="ARK", canvas_id="CID", page_label="P1",
        range_label="R1", description="desc", source_url="url", atk_version="X"
    )
    assert meta["UA"] == "UA"
    assert "_json" in meta

def test_build_image_metadata_minimal():
    meta = tr.build_image_metadata()
    assert "Software" in meta
    assert "_json" in meta


# --- _exif_from_meta ---
def test_exif_from_meta_with_fields():
    meta = {"Description": "desc", "UA": "ua"}
    exif = tr._exif_from_meta(meta)
    assert tr.piexif.ImageIFD.ImageDescription in exif["0th"]

def test_exif_from_meta_empty():
    exif = tr._exif_from_meta({})
    assert exif["0th"] == {}


# --- _validate_params ---
def test_validate_params_dir_not_found():
    with pytest.raises(FileNotFoundError):
        tr.TileRebuilder("no_such_dir", "out.png", (1, 1), (1, 1))

def test_validate_params_invalid_grid(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    with pytest.raises(ValueError):
        tr.TileRebuilder(str(tmp_path), "out.png", (0, 1), (1, 1))

def test_validate_params_invalid_tile(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    with pytest.raises(ValueError):
        tr.TileRebuilder(str(tmp_path), "out.png", (1, 1), (0, 1))


# --- load_tiles ---
def test_load_tiles_with_valid_and_invalid(tmp_path):
    make_dummy_image(tmp_path / "a.png")
    (tmp_path / "b.txt").write_text("not an image")
    reb = tr.TileRebuilder(str(tmp_path), "out.png", (1, 1), (10, 10))
    tiles = reb.load_tiles()
    assert len(tiles) == 1
    assert isinstance(tiles[0], Image.Image)


# --- rebuild ---
def test_rebuild_with_warning(tmp_path, caplog):
    make_dummy_image(tmp_path / "a.png")
    reb = tr.TileRebuilder(str(tmp_path), "out.png", (2, 1), (10, 10))
    img = reb.rebuild()
    assert isinstance(img, Image.Image)
    assert "Numero di tile" in caplog.text


# --- save ---
def test_save_creates_image_and_sidecar(tmp_path):
    make_dummy_image(tmp_path / "a.png")
    metadata = {"Key": "Value", "_json": '{"Key":"Value"}'}
    reb = tr.TileRebuilder(str(tmp_path), str(tmp_path / "out.png"), (1, 1), (10, 10), metadata=metadata)
    reb.save()
    assert (tmp_path / "out.png").exists()
    assert (tmp_path / "out.json").exists()
    data = json.loads((tmp_path / "out.json").read_text())
    assert data["Key"] == "Value"


# --- run() ---
def test_run_invokes_save(monkeypatch, tmp_path):
    make_dummy_image(tmp_path / "a.png")
    called = {}
    def fake_save(self):
        called["yes"] = True
    monkeypatch.setattr(tr.TileRebuilder, "save", fake_save)

    # Simuliamo argv come in uso reale
    argv = [
        "prog",
        str(tmp_path),
        str(tmp_path / "out.png"),
        "--columns", "1",
        "--rows", "1",
        "--tile-width", "10",
        "--tile-height", "10"  # forma lunga, nessun conflitto
    ]
    monkeypatch.setattr("sys.argv", argv)

    tr.run()
    assert called.get("yes") is True

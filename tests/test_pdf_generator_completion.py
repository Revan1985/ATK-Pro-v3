import os
import pytest
import src.pdf_generator as pg
from PIL import Image

def test_sort_modes_and_invalid_images(monkeypatch, tmp_path):
    # Crea due immagini dummy
    img_a = tmp_path / "a_img.png"
    img_b = tmp_path / "b_img.png"
    Image.new("RGB", (10, 10)).save(img_a)
    Image.new("RGB", (10, 10)).save(img_b)

    # Forza sort=name
    args = {"input": str(tmp_path), "output": tmp_path / "out_name.pdf", "sort": "name"}
    result_name = pg.run(args)
    assert result_name["status"] == "ok"

    # Forza sort=mtime con mock di getmtime
    monkeypatch.setattr(os.path, "getmtime", lambda p: 1 if "b_img" in p else 2)
    args["output"] = tmp_path / "out_mtime.pdf"
    args["sort"] = "mtime"
    result_mtime = pg.run(args)
    assert result_mtime["status"] == "ok"

def test_all_images_invalid_triggers_no_valid_images(monkeypatch, tmp_path):
    # Crea un file con estensione immagine ma contenuto non valido
    bad_img = tmp_path / "bad.png"
    bad_img.write_text("non è un'immagine")

    # Mock Image.open per sollevare eccezione → forza il ramo no_valid_images
    def raise_error(*a, **k): raise OSError("file corrotto")
    monkeypatch.setattr(pg.Image, "open", raise_error)

    args = {"input": str(tmp_path), "output": tmp_path / "out.pdf", "sort": "name"}
    result = pg.run(args)
    assert result["status"] == "error"
    assert result["reason"] == "no_valid_images"

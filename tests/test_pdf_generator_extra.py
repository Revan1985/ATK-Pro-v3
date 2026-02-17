import os
import pytest
from PIL import Image
import src.pdf_generator as pg

class DummyImage:
    def save(self, *a, **k): pass

def test_sort_by_name_and_mtime(monkeypatch, tmp_path):
    # Crea due immagini con nomi diversi
    img1 = tmp_path / "b_img.png"
    img2 = tmp_path / "a_img.png"
    Image.new("RGB", (10, 10)).save(img1)
    Image.new("RGB", (10, 10)).save(img2)

    # Mock getmtime per invertire l'ordine
    monkeypatch.setattr(os.path, "getmtime", lambda p: 1 if "b_img" in p else 2)

    # sort=name
    args = {"input": str(tmp_path), "output": tmp_path / "out1.pdf", "sort": "name"}
    pg.run(args)

    # sort=mtime
    args["sort"] = "mtime"
    pg.run(args)

def test_invalid_image_skipped(monkeypatch, tmp_path):
    # File immagine valido
    img1 = tmp_path / "img1.png"
    Image.new("RGB", (10, 10)).save(img1)
    # File corrotto
    bad_img = tmp_path / "img2.png"
    bad_img.write_text("non è un'immagine")

    args = {"input": str(tmp_path), "output": tmp_path / "out2.pdf", "sort": "name"}
    result = pg.run(args)
    assert result["status"] == "ok"
    assert result["pages"] == 1

def test_no_valid_images(tmp_path):
    # Nessuna immagine valida
    bad_img = tmp_path / "img.png"
    bad_img.write_text("non è un'immagine")

    args = {"input": str(tmp_path), "output": tmp_path / "out3.pdf", "sort": "name"}
    result = pg.run(args)
    assert result["status"] == "error"
    assert result["reason"] == "no_valid_images"

def test_default_output_filename(monkeypatch, tmp_path):
    img1 = tmp_path / "img1.png"
    Image.new("RGB", (10, 10)).save(img1)

    args = {"input": str(tmp_path), "output": None, "sort": "name"}
    result = pg.run(args)
    assert result["status"] == "ok"
    assert result["output"].endswith("_bundle.pdf")

def test_with_metadata(monkeypatch, tmp_path):
    img1 = tmp_path / "img1.png"
    Image.new("RGB", (10, 10)).save(img1)

    args = {
        "input": str(tmp_path),
        "output": tmp_path / "out4.pdf",
        "sort": "name",
        "title": "Titolo Test",
        "author": "Autore Test",
        "subject": "Soggetto Test",
        "keywords": "kw1,kw2"
    }
    result = pg.run(args)
    assert result["status"] == "ok"

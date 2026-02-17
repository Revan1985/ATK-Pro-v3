import pytest
import src.pdf_generator as pg
from PIL import Image

def test_pdf_generator_no_images(monkeypatch):
    monkeypatch.setattr("src.pdf_generator._collect_images_priority", lambda _: [])
    result = pg.run({"input": "output", "output": "test.pdf"})
    assert result["status"] == "error" and result["reason"] == "no_images_found"

def test_pdf_generator_no_valid_images(monkeypatch):
    monkeypatch.setattr("src.pdf_generator._collect_images_priority", lambda _: ["img1.jpg"])
    monkeypatch.setattr("src.pdf_generator.Image.open", lambda _: (_ for _ in ()).throw(Exception("errore")))
    result = pg.run({"input": "output", "output": "test.pdf"})
    assert result["status"] == "error" and result["reason"] == "no_valid_images"

def test_pdf_generator_valueerror(monkeypatch):
    monkeypatch.setattr("src.pdf_generator._collect_images_priority", lambda _: ["img1.jpg"])
    def fake_open(path):
        if not hasattr(fake_open, "called"):
            fake_open.called = True
            return type("I", (), {"verify": lambda self: None})()
        raise ValueError("errore")
    monkeypatch.setattr("src.pdf_generator.Image.open", fake_open)
    result = pg.run({"input": "output", "output": "test.pdf"})
    assert result["status"] == "error" and result["reason"] == "no_valid_images"

def test_pdf_generator_success(monkeypatch):
    # Creiamo una vera immagine PIL in memoria
    real_img = Image.new("RGB", (100, 100))
    real_img.verify = lambda: None  # bypassa la validazione

    monkeypatch.setattr("src.pdf_generator._collect_images_priority", lambda _: ["img1.jpg"])
    monkeypatch.setattr("src.pdf_generator.Image.open", lambda _: real_img)

    result = pg.run({"input": "output", "output": "test.pdf"})
    assert result is None or result.get("status") == "ok"

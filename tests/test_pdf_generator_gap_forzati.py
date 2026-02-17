import pytest
from PIL import Image
import src.pdf_generator as pg

def test_force_convert_oserror(monkeypatch, tmp_path):
    """Forza ramo difensivo in pdf_generator.run simulando errore in convert()"""
    # Creiamo un'immagine fittizia e la salviamo come input
    img = Image.new("RGB", (5, 5))
    img_path = tmp_path / "img.png"
    img.save(img_path)

    # Patchiamo convert per sollevare OSError
    monkeypatch.setattr(Image.Image, "convert", lambda self, mode: (_ for _ in ()).throw(OSError("fail convert")))

    args = {"input": str(tmp_path), "output": str(tmp_path / "out.pdf")}
    result = pg.run(args)

    # Deve restituire errore 'no_valid_images' perché tutte le immagini falliscono
    assert result["status"] == "error"
    assert result["reason"] in ("no_valid_images", "save_failed: fail convert")

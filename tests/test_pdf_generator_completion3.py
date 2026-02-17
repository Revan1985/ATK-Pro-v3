import os
import src.pdf_generator as pg
from PIL import Image

# --- Copertura riga 35 e 40 ---
def test_sort_name_and_mtime(monkeypatch, tmp_path):
    # Creo due immagini valide
    img_a = tmp_path / "a_img.png"
    img_b = tmp_path / "b_img.png"
    Image.new("RGB", (10, 10)).save(img_a)
    Image.new("RGB", (10, 10)).save(img_b)

    # sort=name → riga 35
    args = {"input": str(tmp_path), "output": tmp_path / "out_name.pdf", "sort": "name"}
    assert pg.run(args)["status"] == "ok"

    # sort=mtime → riga 40
    monkeypatch.setattr(os.path, "getmtime", lambda p: 1 if "b_img" in p else 2)
    args["output"] = tmp_path / "out_mtime.pdf"
    args["sort"] = "mtime"
    assert pg.run(args)["status"] == "ok"

# --- Copertura riga 46 e 51 ---
def test_verify_and_convert_exceptions(monkeypatch, tmp_path):
    # Creo due immagini valide come base
    img1 = tmp_path / "img1.png"
    img2 = tmp_path / "img2.png"
    Image.new("RGB", (10, 10)).save(img1)
    Image.new("RGB", (10, 10)).save(img2)

    class FakeImage:
        def __init__(self, path):
            self.path = path
        def verify(self):
            if "img1" in self.path:
                raise OSError("verify failed")  # riga 46
        def convert(self, mode):
            raise OSError("convert failed")    # riga 51

    def fake_open(path, *a, **k):
        return FakeImage(path)

    monkeypatch.setattr(pg.Image, "open", fake_open)

    args = {"input": str(tmp_path), "output": tmp_path / "out_invalid.pdf"}
    result = pg.run(args)
    assert result["status"] == "error"
    assert result["reason"] == "no_valid_images"

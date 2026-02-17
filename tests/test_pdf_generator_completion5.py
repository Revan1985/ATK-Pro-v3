import os
import src.pdf_generator as pg
from PIL import Image

def test_cover_all_remaining_branches(monkeypatch, tmp_path):
    # --- Parte 1: ordinamenti (35 e 40) ---
    valid_dir = tmp_path / "valid_imgs"
    valid_dir.mkdir()
    img_a = valid_dir / "a_img.png"
    img_b = valid_dir / "b_img.png"
    Image.new("RGB", (10, 10)).save(img_a)
    Image.new("RGB", (10, 10)).save(img_b)

    # sort=name
    args = {"input": str(valid_dir), "output": valid_dir / "out_name.pdf", "sort": "name"}
    assert pg.run(args)["status"] == "ok"

    # sort=mtime
    monkeypatch.setattr(os.path, "getmtime", lambda p: 1 if "b_img" in p else 2)
    args["output"] = valid_dir / "out_mtime.pdf"
    args["sort"] = "mtime"
    assert pg.run(args)["status"] == "ok"

    # --- Parte 2: eccezioni distinte (46 e 51) ---
    bad_dir = tmp_path / "bad_imgs"
    bad_dir.mkdir()
    img1 = bad_dir / "img1.png"
    img2 = bad_dir / "img2.png"
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

    args = {"input": str(bad_dir), "output": bad_dir / "out_invalid.pdf"}
    result = pg.run(args)
    assert result["status"] == "error"
    assert result["reason"] == "no_valid_images"

def test_pdf_generator_completion7(monkeypatch, tmp_path):
    from src import pdf_generator as pg
    import os
    from PIL import Image

    # Setup immagini reali
    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    img1 = img_dir / "img1.png"
    img2 = img_dir / "img2.png"
    Image.new("RGB", (10, 10)).save(img1)
    Image.new("RGB", (10, 10)).save(img2)

    # Mock getmtime → forza sort=mtime
    monkeypatch.setattr(os.path, "getmtime", lambda p: 100 if "img1" in p else 10)

    # Mock Image.open → eccezioni mirate
    class FakeImage:
        def __init__(self, path): self.path = path
        def verify(self):
            if "img1" in self.path:
                raise OSError("verify failed")  # riga 46
        def convert(self, mode):
            raise OSError("convert failed")     # riga 51

    def fake_open(path, *a, **k): return FakeImage(path)
    monkeypatch.setattr(pg.Image, "open", fake_open)

    # sort=name → riga 35
    args = {"input": str(img_dir), "output": img_dir / "out_name.pdf", "sort": "name"}
    result1 = pg.run(args)
    assert result1["status"] == "error"

    # sort=mtime → riga 40
    args["output"] = img_dir / "out_mtime.pdf"
    args["sort"] = "mtime"
    result2 = pg.run(args)
    assert result2["status"] == "error"

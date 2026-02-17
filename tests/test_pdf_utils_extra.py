import os
import pytest
from pdf_utils import open_image_safe, normalize_image_mode, create_pdf_from_images, enrich_pdf_metadata

# === Copertura test ===
# ✅ Validato

def test_open_image_safe_eccezione(monkeypatch):
    def fake_open(path):
        raise IOError("Errore apertura")
    monkeypatch.setattr("pdf_utils.Image.open", fake_open)
    assert open_image_safe("fake.png") is None

@pytest.mark.parametrize("mode", ["LA", "CMYK"])
def test_normalize_image_mode_vari(monkeypatch, mode):
    from PIL import Image
    img = Image.new(mode, (10, 10))
    result = normalize_image_mode(img)
    assert result.mode in ("L", "RGB")

def test_create_pdf_from_images_tutte_none(monkeypatch, tmp_path):
    monkeypatch.setattr("pdf_utils.open_image_safe", lambda p: None)
    out = tmp_path / "out.pdf"
    assert create_pdf_from_images(["a.png", "b.png"], str(out)) is None
    assert not out.exists()

def test_create_pdf_from_images_eccezione_salvataggio(monkeypatch, tmp_path):
    from PIL import Image
    img = Image.new("RGB", (10, 10))
    path = tmp_path / "img.png"
    img.save(path)
    def fake_save(*a, **k):
        raise IOError("Errore salvataggio")
    monkeypatch.setattr("pdf_utils.Image.Image.save", fake_save)
    assert create_pdf_from_images([str(path)], str(tmp_path / "out.pdf")) is None

def test_enrich_pdf_metadata_eccezione_lettura(tmp_path, monkeypatch):
    pdf_path = tmp_path / "fake.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")
    monkeypatch.setattr("pdf_utils.PdfReader", lambda _: (_ for _ in ()).throw(IOError("Errore lettura")))
    assert enrich_pdf_metadata(str(pdf_path), "t", "s", "ua", "ark") is False

def test_enrich_pdf_metadata_eccezione_scrittura(tmp_path, monkeypatch):
    from PIL import Image
    img_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10)).save(img_path)
    pdf_path = tmp_path / "base.pdf"
    create_pdf_from_images([str(img_path)], str(pdf_path))

    class FakeWriter:
        def __init__(self, *a, **k): pass
        def write(self, *a, **k): raise IOError("Errore scrittura")
        def add_metadata(self, *a, **k): pass

    monkeypatch.setattr("pdf_utils.PdfWriter", lambda: FakeWriter())
    assert enrich_pdf_metadata(str(pdf_path), "t", "s", "ua", "ark") is False

def test_create_pdf_from_images_close_eccezione(monkeypatch, tmp_path):
    from PIL import Image

    # Immagine valida per far partire il flusso
    img_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10)).save(img_path)

    # Apri normalmente
    real_img = Image.open(img_path)

    # Wrappa l'immagine per simulare eccezione in close()
    class ImgWrapper:
        def __init__(self, im):
            self.im = im
        def save(self, *a, **k): return self.im.save(*a, **k)
        def close(self): raise RuntimeError("Errore in close()")

    # Monkeypatch open_image_safe per restituire il wrapper
    monkeypatch.setattr("pdf_utils.open_image_safe", lambda p: ImgWrapper(real_img))

    # Esegui: deve arrivare al finally e ignorare l'eccezione
    out_pdf = tmp_path / "out.pdf"
    assert create_pdf_from_images([str(img_path)], str(out_pdf)) is None or out_pdf.exists()

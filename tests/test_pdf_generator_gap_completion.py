import pytest
import src.pdf_generator as pg
from PIL import Image

def test_pdf_generator_save_failure(monkeypatch, tmp_path):
    # Creiamo una vera immagine PIL in memoria
    real_img = Image.new("RGB", (100, 100))
    real_img.verify = lambda: None  # bypassa la validazione

    # Forziamo la raccolta immagini a restituire un file fittizio
    monkeypatch.setattr("src.pdf_generator._collect_images_priority", lambda _: ["img1.jpg"])
    # Forziamo Image.open a restituire la nostra immagine valida
    monkeypatch.setattr("src.pdf_generator.Image.open", lambda _: real_img)

    # Monkeypatchiamo il metodo save per simulare un errore in fase di salvataggio PDF
    def fake_save(self, *args, **kwargs):
        raise OSError("save failed")

    monkeypatch.setattr(Image.Image, "save", fake_save)

    result = pg.run({"input": "imgs", "output": str(tmp_path / "out.pdf")})

    assert result["status"] == "error"
    assert "save" in result["reason"].lower()

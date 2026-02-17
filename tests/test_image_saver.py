# tests/test_image_saver.py
from PIL import Image
import image_saver

def test_save_image_variants(monkeypatch, tmp_path):
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    saved_files = []

    def fake_save(self, path, fmt, **kwargs):
        saved_files.append((path, fmt))

    monkeypatch.setattr("PIL.Image.Image.save", fake_save)

    image_saver.save_image_variants(img, tmp_path, "test_img", ["JPEG", "PNG", "TIFF"], meta={"Author": "Test"})
    assert any("JPEG" in fmt for _, fmt in saved_files)
    assert any("PNG" in fmt for _, fmt in saved_files)
    assert any("TIFF" in fmt for _, fmt in saved_files)

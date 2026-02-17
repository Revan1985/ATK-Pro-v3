import pytest
from PIL import Image
import src.metadata_utils as mu

def test_force_always_typeerror(monkeypatch, tmp_path):
    """Forza ramo difensivo TIFF sollevando sempre TypeError"""
    img = Image.new("RGB", (5, 5))
    out = tmp_path / "f.tiff"
    monkeypatch.setattr(Image.Image, "save", lambda *a, **kw: (_ for _ in ()).throw(TypeError("always fail")))
    with pytest.raises(TypeError):
        mu.embed_metadata_and_save(img, str(out), mu.build_image_metadata("x"))

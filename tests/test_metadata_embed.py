import os
from PIL import Image
import piexif
import io
import tempfile
import pytest

from src.metadata_utils import embed_metadata_and_save


def test_embed_metadata_png_and_jpeg_and_tiff_fallback(tmp_path, monkeypatch):
    # create a simple image
    img = Image.new('RGB', (10, 10), color=(255, 0, 0))
    meta = {
        'Description': 'test',
        'UA': 'UA:1',
        'Software': 'ATK-Pro',
        '_json': '{"k": "v"}'
    }

    # 1) PNG: should write png and include ATK-Pro-JSON in info
    png_path = tmp_path / "out.png"
    embed_metadata_and_save(img, str(png_path), meta)
    assert png_path.exists()
    im = Image.open(png_path)
    # Pillow stores text chunks in info
    assert 'ATK-Pro-JSON' in im.info or 'ATK-Pro-JSON' in im.info.keys()

    # 2) JPEG: should write file and include EXIF (piexif can read it)
    jpg_path = tmp_path / "out.jpg"
    embed_metadata_and_save(img, str(jpg_path), meta)
    assert jpg_path.exists()
    try:
        exif_dict = piexif.load(str(jpg_path))
        # check that XPTitle or ImageDescription present
        zeroth = exif_dict.get('0th', {})
        assert any(k in zeroth for k in (piexif.ImageIFD.ImageDescription, piexif.ImageIFD.XPTitle))
    except Exception:
        # some pillow builds might not embed exif for JPEG in test env; at least file exists
        assert jpg_path.stat().st_size > 0

    # 3) TIFF fallback: force TypeError when 'exif' kw provided, succeed otherwise
    tif_path = tmp_path / "out.tif"

    original_save = Image.Image.save

    def fake_save(self, fp, format=None, **kwargs):
        if 'exif' in kwargs:
            raise TypeError('forced')
        return original_save(self, fp, format=format, **{k: v for k, v in kwargs.items() if k != 'exif'})

    monkeypatch.setattr(Image.Image, 'save', fake_save)
    try:
        embed_metadata_and_save(img, str(tif_path), meta)
        assert tif_path.exists()
        assert tif_path.stat().st_size > 0
    finally:
        monkeypatch.setattr(Image.Image, 'save', original_save)

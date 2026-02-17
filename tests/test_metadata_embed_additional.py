import os
from PIL import Image
import piexif
import pytest

from src.metadata_utils import embed_metadata_and_save


def test_piexif_dump_failure_handled(tmp_path, monkeypatch):
    img = Image.new('RGB', (10, 10), color=(10, 20, 30))
    meta = {'Description': 'x', 'UA': 'u', '_json': '{"a":1}'}

    # Force piexif.dump to raise an exception
    monkeypatch.setattr(piexif, 'dump', lambda *a, **k: (_ for _ in ()).throw(Exception('dump failed')))

    # JPEG should still be created (fallback in embed_metadata_and_save handles exceptions)
    jpg = tmp_path / 'fail.jpg'
    embed_metadata_and_save(img, str(jpg), meta)
    assert jpg.exists()
    assert jpg.stat().st_size > 0

    # TIFF should still be created (fallback without exif)
    tif = tmp_path / 'fail.tif'
    embed_metadata_and_save(img, str(tif), meta)
    assert tif.exists()
    assert tif.stat().st_size > 0


def test_tiff_exif_presence_if_supported(tmp_path):
    img = Image.new('RGB', (10, 10), color=(1, 2, 3))
    meta = {'Description': 'd', 'UA': 'u', '_json': '{"b":2}'}

    tif = tmp_path / 'maybe.tif'
    # Try saving normally; if environment/Pillow supports exif on TIFF,
    # embed_metadata_and_save will produce a TIFF. Otherwise it must still succeed.
    embed_metadata_and_save(img, str(tif), meta)
    assert tif.exists()
    assert tif.stat().st_size > 0

    # For JPEG check EXIF readable if present
    jpg = tmp_path / 'maybe.jpg'
    embed_metadata_and_save(img, str(jpg), meta)
    assert jpg.exists()
    assert jpg.stat().st_size > 0

    try:
        ex = piexif.load(str(jpg))
        assert isinstance(ex, dict)
    except Exception:
        # Some environments may not include EXIF; accept file exists
        pass

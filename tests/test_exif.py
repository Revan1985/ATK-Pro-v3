import piexif
import pytest
from src.tile_rebuilder import _exif_from_meta

def test_exif_empty():
    exif = _exif_from_meta({})
    assert exif["0th"] == {}
    assert exif["Exif"] == {}

def test_exif_with_description_and_ua():
    meta = {"Description":"desc","UA":"dev"}
    exif = _exif_from_meta(meta)
    zeroth = exif["0th"]
    # Piexif.ImageIFD.ImageDescription == 270
    assert zeroth[piexif.ImageIFD.ImageDescription] == b"desc"
    # Piexif.ImageIFD.Artist == 315
    assert zeroth[piexif.ImageIFD.Artist] == b"dev"

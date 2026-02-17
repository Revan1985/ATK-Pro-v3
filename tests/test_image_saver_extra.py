# tests/test_image_saver_extra.py
from pathlib import Path
from PIL import Image
import image_saver
import os

def _exists_any(path_without_ext: Path, exts):
    for ext in exts:
        if (path_without_ext.parent / f"{path_without_ext.name}.{ext}").exists():
            return True
    return False

def test_save_variants_with_and_without_meta(tmp_path):
    img = Image.new("RGB", (16, 16), color=(10, 20, 30))

    # 1) Salvataggio senza metadati
    base1 = "no_meta"
    image_saver.save_image_variants(
        img,
        str(tmp_path),
        base1,
        ["JPEG", "PNG", "TIFF"],  # JPEG, non JPG
        meta=None
    )
    # In ATK-Pro lo standard è .jpg; per robustezza accettiamo anche .jpeg se mai usato
    assert _exists_any(tmp_path / base1, ["jpg", "jpeg"])
    assert (tmp_path / f"{base1}.png").exists()
    assert (tmp_path / f"{base1}.tif").exists()

    # 2) Salvataggio con metadati minimi
    base2 = "with_meta"
    meta = {"Author": "ATK-Pro", "Description": "Test save"}
    image_saver.save_image_variants(
        img,
        str(tmp_path),
        base2,
        ["JPEG", "PNG", "TIFF"],  # JPEG, non JPG
        meta=meta
    )
    assert _exists_any(tmp_path / base2, ["jpg", "jpeg"])
    assert (tmp_path / f"{base2}.png").exists()
    assert (tmp_path / f"{base2}.tif").exists()

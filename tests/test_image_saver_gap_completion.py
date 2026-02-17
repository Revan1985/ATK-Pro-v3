from PIL import Image
import image_saver

def test_save_image_variants_no_formats(tmp_path):
    """Nessun formato richiesto: non deve salvare nulla."""
    img = Image.new("RGB", (8, 8), color=(0, 0, 0))
    image_saver.save_image_variants(img, str(tmp_path), "nofmt", [], meta=None)
    # Nessun file creato
    assert not any(tmp_path.iterdir())

def test_save_image_variants_only_png(tmp_path):
    """Solo PNG senza metadati."""
    img = Image.new("RGB", (8, 8), color=(0, 0, 0))
    image_saver.save_image_variants(img, str(tmp_path), "onlypng", ["PNG"], meta=None)
    assert (tmp_path / "onlypng.png").exists()

def test_save_image_variants_only_jpeg(tmp_path):
    """Solo JPEG senza metadati."""
    img = Image.new("RGB", (8, 8), color=(0, 0, 0))
    image_saver.save_image_variants(img, str(tmp_path), "onlyjpeg", ["JPEG"], meta=None)
    # In ATK-Pro lo standard è .jpg, ma accettiamo anche .jpeg
    assert any((tmp_path / "onlyjpeg").with_suffix(ext).exists() for ext in [".jpg", ".jpeg"])

def test_save_image_variants_only_tiff(tmp_path):
    """Solo TIFF senza metadati."""
    img = Image.new("RGB", (8, 8), color=(0, 0, 0))
    image_saver.save_image_variants(img, str(tmp_path), "onlytiff", ["TIFF"], meta=None)
    assert (tmp_path / "onlytiff.tif").exists()

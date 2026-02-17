from unittest.mock import MagicMock, patch
import src.metadata_utils as mu

def test_embed_metadata_and_save_tiff_typeerror(monkeypatch):
    """Simula il caso TIFF in cui Pillow non supporta exif= e solleva TypeError.
    Atteso: fallback a salvataggio senza exif.
    """
    img = MagicMock()
    meta = mu.build_image_metadata(description="Desc")

    # piexif.dump restituisce bytes validi
    monkeypatch.setattr("src.metadata_utils.piexif.dump", lambda _: b"exifbytes")

    # Prima chiamata a save con exif → solleva TypeError
    # Seconda chiamata senza exif → va a buon fine
    def fake_save(path, *args, **kwargs):
        if "exif" in kwargs:
            raise TypeError("unsupported exif")
        return None

    img.save.side_effect = fake_save

    mu.embed_metadata_and_save(img, "out.tiff", meta)

    # Verifica che sia stato tentato prima con exif e poi senza
    calls = [call.kwargs for call in img.save.call_args_list]
    assert any("exif" in c for c in calls)   # primo tentativo con exif
    assert any("exif" not in c for c in calls)  # fallback senza exif

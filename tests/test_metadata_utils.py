import json
import pytest
from unittest.mock import patch, MagicMock, mock_open, PropertyMock
import src.metadata_utils as mu


# ---------------------------
# build_image_metadata
# ---------------------------

@pytest.mark.parametrize("kwargs,expected_keys", [
    ({}, {"Software", "ATK-Pro-Version", "_json"}),
    (
        {
            "ua": "UA_001",
            "ark": "ARK1",
            "canvas_id": "CID1",
            "page_label": "P1",
            "range_label": "R1",
            "description": "Desc",
            "source_url": "URL"
        },
        {"UA", "ARK", "CanvasID", "Page", "Range", "Description", "Source",
         "Software", "ATK-Pro-Version", "_json"}
    )
])
def test_build_image_metadata(kwargs, expected_keys):
    meta = mu.build_image_metadata(**kwargs)
    assert expected_keys.issubset(meta.keys())
    # _json deve essere un JSON valido
    json.loads(meta["_json"])


# ---------------------------
# _exif_from_meta
# ---------------------------

def test_exif_from_meta_complete_and_partial():
    meta = mu.build_image_metadata(
        ua="UA_001", ark="ARK1", canvas_id="CID1", description="Desc"
    )
    exif_data = mu._exif_from_meta(meta)
    assert "0th" in exif_data and isinstance(exif_data["0th"], dict)
    assert any(isinstance(v, bytes) for v in exif_data["0th"].values())

    # Parziale: solo UA
    meta2 = {"UA": "UA_002", "Software": "Soft"}
    exif_data2 = mu._exif_from_meta(meta2)
    assert mu.piexif.ImageIFD.Artist in exif_data2["0th"]


# ---------------------------
# _save_sidecar_json_once
# ---------------------------

def test_save_sidecar_json_once_new_existing_error(tmp_path):
    meta = {"_json": '{"a": 1}'}
    base_filename = "file1"

    # Caso nuovo file
    with patch("builtins.open", mock_open()) as m, patch("os.path.exists", return_value=False):
        mu._save_sidecar_json_once(str(tmp_path), base_filename, meta)
        m.assert_called_once()

    # Caso file già esistente
    with patch("builtins.open", mock_open()) as m, patch("os.path.exists", return_value=True):
        mu._save_sidecar_json_once(str(tmp_path), base_filename, meta)
        m.assert_not_called()

    # Caso eccezione in open
    with patch("builtins.open", side_effect=OSError("fail")), patch("os.path.exists", return_value=False):
        mu._save_sidecar_json_once(str(tmp_path), base_filename, meta)  # non deve sollevare


# ---------------------------
# embed_metadata_and_save
# ---------------------------

@pytest.mark.parametrize("ext", [".jpg", ".jpeg"])
def test_embed_metadata_and_save_jpeg(ext):
    img = MagicMock()
    img.convert.return_value = img  # fondamentale per tracciare save
    meta = mu.build_image_metadata(description="Desc")
    with patch("src.metadata_utils.piexif.dump", return_value=b"exifbytes") as dump_mock:
        mu.embed_metadata_and_save(img, f"out{ext}", meta)
        dump_mock.assert_called_once()
        img.convert.assert_called_with("RGB")
        img.save.assert_called_once()
        assert "exif" in img.save.call_args.kwargs


def test_embed_metadata_and_save_png():
    img = MagicMock()
    meta = mu.build_image_metadata(description="Desc", ua="UA_001")
    with patch("src.metadata_utils.PngImagePlugin.PngInfo") as pnginfo_cls:
        pnginfo = MagicMock()
        pnginfo_cls.return_value = pnginfo
        mu.embed_metadata_and_save(img, "out.png", meta)
        pnginfo.add_text.assert_any_call("Description", "Desc")
        img.save.assert_called_once()


def test_embed_metadata_and_save_tiff_with_and_without_exif():
    img = MagicMock()
    meta = mu.build_image_metadata(description="Desc")

    # Con EXIF
    with patch("src.metadata_utils.piexif.dump", return_value=b"exifbytes"):
        mu.embed_metadata_and_save(img, "out.tiff", meta)
        img.save.assert_called_with("out.tiff", "TIFF", compression="tiff_lzw", exif=b"exifbytes")

    # Senza EXIF (dump solleva)
    with patch("src.metadata_utils.piexif.dump", side_effect=Exception("no exif")):
        mu.embed_metadata_and_save(img, "out.tiff", meta)
        img.save

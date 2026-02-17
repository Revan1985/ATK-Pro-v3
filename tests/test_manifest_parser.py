import json
import os
from src.manifest_parser import estrai_metadati_da_manifest


def test_estrai_metadati_infer_register(tmp_path):
    manifest = {
        "label": "Registro X",
        "items": [
            {"id": "canvas_1"}, {"id": "canvas_2"}, {"id": "canvas_3"}
        ],
        "rights": "Public Domain",
        "metadata": [
            {"label": "Data", "value": "1850"},
            {"label": "Note", "value": "Test"}
        ]
    }

    p = tmp_path / "manifest_test.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False)

    estrai_metadati_da_manifest(str(p), immagini_generate=["a.png"])

    base = os.path.splitext(os.path.basename(str(p)))[0]
    gen = tmp_path / f"{base}_genealogico.json"
    tec = tmp_path / f"{base}_tecnico.json"

    assert gen.exists()
    assert tec.exists()

    with open(tec, encoding="utf-8") as ft:
        data = json.load(ft)
        assert data.get("numero_canvas") == 3
        assert "canvas_id_list" in data
        assert data.get("diritti") == "Public Domain"


def test_estrai_metadati_with_record_name_creates_subdir(tmp_path):
    manifest = {
        "items": [{"id": "c1"}],
        "metadata": []
    }
    p = tmp_path / "manifest2.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(manifest, f)

    estrai_metadati_da_manifest(str(p), record_prefix="R", record_nome_file="My Record")

    outdir = tmp_path / "My Record"
    assert outdir.exists()
    files = list(outdir.glob("*_tecnico.json"))
    assert len(files) == 1
import json
import builtins
import io
import pytest
from unittest.mock import mock_open, patch
import src.manifest_parser as mp


def make_fake_open(manifest_data_str="{}", manifest_obj=None):
    """
    Restituisce una funzione fake_open che:
    - in lettura ('r') restituisce il contenuto mockato
    - in scrittura ('w') usa la open reale
    """
    real_open = builtins.open
    m = mock_open(read_data=manifest_data_str)

    def fake_open(path, mode="r", encoding=None):
        if "r" in mode:
            return m()
        return real_open(path, mode, encoding=encoding)

    return fake_open


def test_manifest_completo_dict_label(tmp_path, capsys):
    manifest = {
        "label": {"it": ["Titolo Registro"]},
        "metadata": [
            {"label": {"it": ["Data"]}, "value": {"it": ["1900"]}},
            {"label": {"it": ["Formato"]}, "value": {"it": ["TIFF"]}},
        ],
        "items": [{"id": "canvas1"}, {"id": "canvas2"}],
        "rights": "public-domain"
    }

    with patch("builtins.open", side_effect=make_fake_open()), \
         patch("json.load", return_value=manifest):
        mp.estrai_metadati_da_manifest(str(tmp_path / "file.json"))

    genealogico_path = tmp_path / "file_genealogico.json"
    tecnico_path = tmp_path / "file_tecnico.json"
    assert genealogico_path.exists()
    assert tecnico_path.exists()

    genealogico = json.loads(genealogico_path.read_text(encoding="utf-8"))
    tecnico = json.loads(tecnico_path.read_text(encoding="utf-8"))
    assert "Titolo Registro" in genealogico["titolo"] or genealogico["titolo"] == "Titolo Registro"
    assert tecnico["numero_canvas"] == 2
    assert tecnico["diritti"] == "public-domain"

    out = capsys.readouterr().out
    assert "📄 Metadati genealogici salvati" in out
    assert "📄 Metadati tecnici salvati" in out


def test_manifest_label_string(tmp_path):
    manifest = {"label": "Titolo Semplice", "metadata": []}

    with patch("builtins.open", side_effect=make_fake_open()), \
         patch("json.load", return_value=manifest):
        mp.estrai_metadati_da_manifest(str(tmp_path / "file.json"))

    genealogico = json.loads((tmp_path / "file_genealogico.json").read_text(encoding="utf-8"))
    assert genealogico["titolo"] == "Titolo Semplice"


def test_manifest_senza_metadata(tmp_path):
    manifest = {"label": "Titolo", "items": []}

    with patch("builtins.open", side_effect=make_fake_open()), \
         patch("json.load", return_value=manifest):
        mp.estrai_metadati_da_manifest(str(tmp_path / "file.json"))

    genealogico = json.loads((tmp_path / "file_genealogico.json").read_text(encoding="utf-8"))
    assert list(genealogico.keys()) == ["titolo"]


def test_manifest_con_immagini_generate(tmp_path):
    manifest = {"label": "Titolo", "metadata": []}
    immagini = ["img1.jpg", "doc.pdf"]

    with patch("builtins.open", side_effect=make_fake_open()), \
         patch("json.load", return_value=manifest):
        mp.estrai_metadati_da_manifest(str(tmp_path / "file.json"), immagini_generate=immagini)

    genealogico = json.loads((tmp_path / "file_genealogico.json").read_text(encoding="utf-8"))
    tecnico = json.loads((tmp_path / "file_tecnico.json").read_text(encoding="utf-8"))
    assert genealogico["file_associati"] == immagini
    assert tecnico["file_associati"] == immagini


def test_errore_apertura_manifest(capsys):
    with patch("builtins.open", side_effect=FileNotFoundError("missing")):
        mp.estrai_metadati_da_manifest("path inesistente.json")
    out = capsys.readouterr().out
    assert "❌ Errore apertura manifest" in out


def test_errore_parsing_manifest(capsys):
    with patch("builtins.open", side_effect=make_fake_open("{malformed}")), \
         patch("json.load", side_effect=json.JSONDecodeError("err", "doc", 0)):
        mp.estrai_metadati_da_manifest("file.json")
    out = capsys.readouterr().out
    assert "❌ Errore apertura manifest" in out


def test_errore_scrittura_manifest(tmp_path, capsys):
    manifest = {"label": "Titolo", "metadata": []}

    real_open = builtins.open
    def fake_open(path, mode="r", encoding=None):
        if "r" in mode:
            return io.StringIO("{}")
        raise OSError("disk full")

    with patch("builtins.open", side_effect=fake_open), \
         patch("json.load", return_value=manifest):
        mp.estrai_metadati_da_manifest(str(tmp_path / "file.json"))

    out = capsys.readouterr().out
    assert "❌ Errore estrazione metadati" in out

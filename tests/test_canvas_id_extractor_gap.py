import pytest
import src.canvas_id_extractor as cie

def test_extract_canvas_id_none(monkeypatch):
    monkeypatch.setattr("src.canvas_id_extractor.extract_canvas_id_from_url", lambda _: None)
    assert cie.extract_canvas_id_from_url("http://example.com") is None

def test_extract_canvas_id_exit(monkeypatch):
    monkeypatch.setattr("src.canvas_id_extractor.extract_canvas_id_from_url", lambda _: (_ for _ in ()).throw(SystemExit))
    with pytest.raises(SystemExit):
        cie.extract_canvas_id_from_url("http://example.com")

def test_extract_ud_canvas_id_none(monkeypatch):
    monkeypatch.setattr("src.canvas_id_extractor.extract_ud_canvas_id_from_infojson_xhr", lambda _: None)
    assert cie.extract_ud_canvas_id_from_infojson_xhr("http://example.com") is None

def test_extract_ud_canvas_id_exit(monkeypatch):
    monkeypatch.setattr("src.canvas_id_extractor.extract_ud_canvas_id_from_infojson_xhr", lambda _: (_ for _ in ()).throw(SystemExit))
    with pytest.raises(SystemExit):
        cie.extract_ud_canvas_id_from_infojson_xhr("http://example.com")

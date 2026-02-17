import pytest
import src.canvas_id_extractor as cie

def test_forzato_playwright_exception(monkeypatch):
    """Test forzato: simuliamo eccezione Playwright -> ritorna None"""
    monkeypatch.setattr(
        "src.canvas_id_extractor.sync_playwright",
        lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    result = cie.extract_ud_canvas_id_from_infojson_xhr("http://fake")
    assert result is None

def test_forzato_no_canvas_found(monkeypatch):
    """Test forzato: simuliamo nessun canvas trovato -> ritorna None"""
    monkeypatch.setattr(cie, "extract_canvas_id_from_url", lambda url: None)
    result = cie.extract_ud_canvas_id("dummy_driver")
    assert result is None

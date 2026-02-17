import pytest
import src.canvas_id_extractor as cie

class DummyFrameMatch:
    def content(self):
        print("DummyFrameMatch.content() chiamato")
        return "<html><body><script>var img='/iiif/2/ABCDEF12/info.json';</script></body></html>"

class DummyPageWithFrame:
    def __init__(self): self._callback = None
    def goto(self, url, wait_until="domcontentloaded", **kwargs):
        # Accept timeout and other kwargs that real Playwright page.goto may receive
        return None
    def content(self): return "<html></html>"
    @property
    def frames(self): return [DummyFrameMatch()]
    def on(self, event, callback): self._callback = callback
    def wait_for_timeout(self, *a, **k):
        if self._callback:
            dummy_resp = type("DummyResp", (), {"status": 200, "url": "http://example.com/"})()
            self._callback(dummy_resp)
    def route(self, pattern, handler): pass
    def locator(self, *a, **k): return type("DummyLocator", (), {"click": lambda *x, **y: None})()

class DummyContextWithFrame:
    def new_page(self): return DummyPageWithFrame()
    def set_default_timeout(self, *a, **k): pass

class DummyBrowserWithFrame:
    def new_context(self, **kwargs): return DummyContextWithFrame()
    def close(self): pass

class DummyPlaywrightWithFrame:
    class chromium:
        @staticmethod
        def launch(**kwargs): return DummyBrowserWithFrame()
    def __enter__(self): return self
    def __exit__(self, *a): pass

def test_extract_ud_canvas_id_match_in_frame(monkeypatch, capsys):
    monkeypatch.setattr(cie, "sync_playwright", lambda: DummyPlaywrightWithFrame())
    result = cie.extract_ud_canvas_id_from_infojson_xhr("http://example.com")
    captured = capsys.readouterr()
    assert "DummyFrameMatch.content() chiamato" in captured.out  # verifica che il frame sia interrogato
    assert result == "ABCDEF12"

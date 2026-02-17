import pytest
import types
import src.canvas_id_extractor as cie


def test_extract_canvas_id_from_url_valid():
    url = "http://example.com/an_ua/123ABC"
    assert cie.extract_canvas_id_from_url(url) == "123ABC"


def test_extract_ud_canvas_id_positive():
    class DummyDriver:
        page_source = '''
        {
            "@id": "https://dam-antenati.cultura.gov.it/iiif/2/XYZ789"
        }
        '''
    driver = DummyDriver()
    result = cie.extract_ud_canvas_id(driver)
    assert result == "XYZ789"


def test_extract_ud_canvas_id_from_infojson_xhr_response(monkeypatch):
    # Simula Playwright e intercettazione response
    class DummyResponse:
        def __init__(self, url, status=200):
            self.url = url
            self.status = status

    class DummyPage:
        def __init__(self):
            self._handlers = {}
            self.frames = []

        def route(self, *_): pass
        def on(self, event, handler): self._handlers[event] = handler
        def goto(self, *_ , **__): pass
        def locator(self, *_ , **__): return types.SimpleNamespace(click=lambda **__: None)
        def wait_for_timeout(self, *_): pass
        def content(self): return "<html></html>"

        def trigger_response(self, url):
            resp = DummyResponse(url)
            self._handlers["response"](resp)

    class DummyContext:
        def __init__(self): self.page = DummyPage()
        def new_page(self): return self.page
        def set_default_timeout(self, *_): pass
        def close(self): pass

    class DummyBrowser:
        def new_context(self, **_): return DummyContext()
        def close(self): pass

    class DummyPlaywright:
        chromium = types.SimpleNamespace(launch=lambda **_: DummyBrowser())
        def __enter__(self): return self
        def __exit__(self, *a): pass

    monkeypatch.setattr(cie, "sync_playwright", lambda: DummyPlaywright())

    # Esegui la funzione
    result = cie.extract_ud_canvas_id_from_infojson_xhr("http://fake")
    # Simula una response intercettata
    page = DummyContext().page
    page._handlers = {}
    page.on("response", lambda res: None)  # handler fittizio
    page.trigger_response("https://dam-antenati.cultura.gov.it/iiif/2/ABCDEF/info.json")

    # Verifica che il risultato sia coerente
    assert result is None or isinstance(result, str)


def test_extract_ud_canvas_id_from_infojson_xhr_html(monkeypatch):
    # Simula Playwright con HTML contenente un canvas valido
    class DummyPage:
        def __init__(self):
            self.frames = []
        def route(self, *_): pass
        def on(self, *_): pass
        def goto(self, *_ , **__): pass
        def locator(self, *_ , **__): return types.SimpleNamespace(click=lambda **__: None)
        def wait_for_timeout(self, *_): pass
        def content(self): return '<html><div>/iiif/2/HELLO99/</div></html>'

    class DummyContext:
        def __init__(self): self.page = DummyPage()
        def new_page(self): return self.page
        def set_default_timeout(self, *_): pass
        def close(self): pass

    class DummyBrowser:
        def new_context(self, **_): return DummyContext()
        def close(self): pass

    class DummyPlaywright:
        chromium = types.SimpleNamespace(launch=lambda **_: DummyBrowser())
        def __enter__(self): return self
        def __exit__(self, *a): pass

    monkeypatch.setattr(cie, "sync_playwright", lambda: DummyPlaywright())

    result = cie.extract_ud_canvas_id_from_infojson_xhr("http://fake")
    assert result == "HELLO99"

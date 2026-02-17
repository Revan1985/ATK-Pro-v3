import pytest
import src.browser_setup as bs

def test_setup_selenium_failure(monkeypatch):
    # Simula errore in webdriver.Chrome
    def fake_chrome(*a, **k):
        raise RuntimeError("Chrome non disponibile")
    monkeypatch.setattr(bs.webdriver, "Chrome", fake_chrome)

    driver = bs.setup_selenium()
    assert driver is None


def test_setup_playwright_failure(monkeypatch):
    # Simula errore in sync_playwright
    def fake_sync_playwright():
        raise RuntimeError("Playwright non disponibile")
    monkeypatch.setattr(bs, "sync_playwright", fake_sync_playwright)

    html = bs.setup_playwright("http://example.com")
    assert html is None

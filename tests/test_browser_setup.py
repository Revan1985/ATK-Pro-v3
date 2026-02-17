import sys
import pytest
from unittest.mock import MagicMock, patch
import src.browser_setup as bs


def test_setup_selenium_crea_driver_con_opzioni():
    fake_driver = MagicMock(name="ChromeDriverMock")
    fake_options = MagicMock(name="OptionsMock")
    fake_service = MagicMock(name="ServiceMock")

    # Patch the dependent classes/constructors inside the module under test
    with patch('src.browser_setup.Options') as mock_options_cls, \
         patch('src.browser_setup.Service') as mock_service_cls, \
         patch('src.browser_setup.webdriver.Chrome') as mock_chrome:

        mock_options_cls.return_value = fake_options
        mock_service_cls.return_value = fake_service
        mock_chrome.return_value = fake_driver

        # esercita la funzione sotto test
        result = bs.setup_selenium()

        mock_options_cls.assert_called_once_with()
        fake_options.add_argument.assert_any_call("--disable-gpu")
        fake_options.add_argument.assert_any_call("--log-level=3")
        mock_service_cls.assert_called_once_with()
        mock_chrome.assert_called_once_with(service=fake_service, options=fake_options)

        assert result is fake_driver


def test_setup_selenium_eccezione_restituisce_none():
    with patch.object(bs.webdriver, "Chrome", side_effect=Exception("Errore driver")):
        result = bs.setup_selenium()
        assert result is None


@pytest.mark.parametrize("url", [
    "http://example.com",
    "https://test.org",
    "https://archivio.fake/manifest"
])
def test_setup_playwright_restituisce_html(url):
    fake_html = f"<html><body>Mocked Page for {url}</body></html>"

    fake_page = MagicMock()
    fake_page.content.return_value = fake_html

    fake_browser = MagicMock()
    fake_context = MagicMock()
    fake_context.new_page.return_value = fake_page
    fake_browser.new_context.return_value = fake_context

    fake_playwright = MagicMock()
    fake_playwright.chromium.launch.return_value = fake_browser

    with patch("src.browser_setup.sync_playwright") as mock_sync:
        mock_sync.return_value.__enter__.return_value = fake_playwright

        result = bs.setup_playwright(url)

        fake_playwright.chromium.launch.assert_called_once_with(headless=True)
        fake_browser.new_context.assert_called_once_with()
        fake_context.new_page.assert_called_once_with()
        fake_page.goto.assert_called_once_with(url, timeout=15000)

        assert result == fake_html


def test_setup_playwright_eccezione_restituisce_none():
    fake_playwright = MagicMock()
    fake_playwright.chromium.launch.side_effect = Exception("Errore Playwright")

    with patch("src.browser_setup.sync_playwright") as mock_sync:
        mock_sync.return_value.__enter__.return_value = fake_playwright

        result = bs.setup_playwright("http://example.com")
        assert result is None

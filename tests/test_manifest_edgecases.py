import requests
import types
import pytest

from src import manifest_utils as mu


def test_find_manifest_in_html_relative():
    html = '<html><head><link rel="manifest" href="manifest.json"></head></html>'
    found = mu._find_manifest_in_html(html)
    assert found is not None
    assert 'manifest' in found


def test_robust_find_manifest_prefers_json():
    html = 'some text https://dam-antenati.cultura.gov.it/antenati/containers/ABC123/manifest.json end'
    found = mu.robust_find_manifest('http://example', html)
    assert found is not None
    assert found.endswith('manifest.json')


def test_download_manifest_non_json(monkeypatch, tmp_path, capsys):
    class DummyResp:
        status_code = 200
        ok = True
        text = 'not-a-json'
        def json(self):
            raise ValueError('no json')
        def raise_for_status(self):
            return None

    def fake_get(url, headers=None, timeout=None):
        return DummyResp()

    monkeypatch.setattr(mu.requests, 'get', fake_get)

    res = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
    captured = capsys.readouterr()
    assert res is None
    assert 'non decodificabile' in captured.out or 'Contenuto manifest non decodificabile' in captured.out


def test_robust_find_manifest_slash_variant():
    # Simulate page_url that needs slash variant to find manifest
    html = ''
    # monkeypatch _http_get to return a response with ok and text containing manifest in slash variant
    class Resp:
        ok = True
        text = 'link https://dam-antenati.cultura.gov.it/antenati/containers/XYZ/manifest'

    monkeypatch = __import__('pytest').MonkeyPatch()
    try:
        monkeypatch.setattr(mu, '_http_get', lambda url, timeout=25: Resp())
        found = mu.robust_find_manifest('http://example')
        assert found is not None
        assert 'manifest' in found
    finally:
        monkeypatch.undo()


def test_robust_find_manifest_in_script_json():
    text = '... "manifest": "https://dam-antenati.cultura.gov.it/antenati/containers/ZZZ/manifest.json" ...'
    found = mu.robust_find_manifest('http://example', text)
    assert found is not None
    assert found.endswith('manifest.json')


def test_download_manifest_server_error_retries(monkeypatch, tmp_path):
    calls = {'n': 0}

    class DummyResp:
        def __init__(self, code):
            self.status_code = code
            self.ok = False
            self.text = ''
        def raise_for_status(self):
            raise Exception('http error')

    def fake_get(url, headers=None, timeout=None):
        calls['n'] += 1
        return DummyResp(500)

    monkeypatch.setattr(mu.requests, 'get', fake_get)
    res = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
    assert res is None
    assert calls['n'] >= 1

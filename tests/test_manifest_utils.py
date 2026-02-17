import pytest
from pathlib import Path
from unittest.mock import patch
import requests
import json
import src.manifest_utils as mu
from src.manifest_utils import find_manifest_url, download_manifest

def test_find_manifest_url_con_manifest_json():
    class MockDriver:
        page_source = (
            "<html><body>"
            "<a href='https://dam-antenati.cultura.gov.it/antenati/containers/xyz789/manifest.json'>manifest</a>"
            "</body></html>"
        )
    result = find_manifest_url(MockDriver())
    assert result == "https://dam-antenati.cultura.gov.it/antenati/containers/xyz789/manifest.json"

def test_find_manifest_url_con_manifest_senza_json():
    class MockDriver:
        page_source = (
            "<html><body>"
            "<a href='https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest'>manifest</a>"
            "</body></html>"
        )
    result = find_manifest_url(MockDriver())
    assert result == "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest"

def test_find_manifest_url_from_page_object():
    class FakePage:
        page_source = '<html><a href="manifest.json">m</a></html>'
    url = mu.find_manifest_url(FakePage())
    assert "manifest.json" in url

def test_download_manifest_url_non_valido(tmp_path):
    result = download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/INVALID/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result is None

@patch("src.manifest_utils.requests.get")
def test_download_manifest_url_valido(mock_get, tmp_path):
    class MockResponse:
        status_code = 200
        def json(self):
            return {"@context": "http://iiif.io/api/presentation/2/context.json"}
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result["@context"] == "http://iiif.io/api/presentation/2/context.json"
    files = list(Path(tmp_path).glob("*.json"))
    assert files and files[0].exists()

@patch("src.manifest_utils.requests.get", side_effect=requests.exceptions.RequestException("Errore di rete"))
def test_download_manifest_eccezione(mock_get, tmp_path):
    result = download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result is None

@patch("src.manifest_utils.requests.get")
def test_manifest_corrotto_v16(mock_get, tmp_path):
    """Gestione manifest corrotto/non decodificabile."""
    class MockResponse:
        status_code = 200
        def json(self): raise json.JSONDecodeError("Errore di parsing", "doc", 0)
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result is None

@patch("src.manifest_utils.requests.get")
def test_manifest_incompleto_v16(mock_get, tmp_path):
    """Gestione manifest incompleto: ritorna comunque il JSON."""
    class MockResponse:
        status_code = 200
        def json(self): return {"sequences": [{}]}
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = mu.download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert isinstance(result, dict)
    assert "sequences" in result
    files = list(Path(tmp_path).glob("*.json"))
    assert files and files[0].exists()

@patch("src.manifest_utils.requests.get")
def test_manifest_chiavi_inattese_v16(mock_get, tmp_path):
    """Gestione manifest con chiavi inattese."""
    class MockResponse:
        status_code = 200
        def json(self): return {"unexpected": "value"}
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = mu.download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result is None or isinstance(result, dict)

@patch("src.manifest_utils.requests.get")
def test_manifest_vuoto_valido(mock_get, tmp_path):
    """Gestione manifest vuoto ma decodificabile."""
    class MockResponse:
        status_code = 200
        def json(self): return {}
        def raise_for_status(self): pass
    mock_get.return_value = MockResponse()
    result = mu.download_manifest(
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest",
        str(tmp_path),
        titolo_doc="test_doc"
    )
    assert result == {}
    files = list(Path(tmp_path).glob("*.json"))
    assert files and files[0].exists()

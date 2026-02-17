import pytest
from src.manifest_utils import download_manifest

def test_download_manifest_malformato(tmp_path):
    manifest_url = "http://example.com/manifest_non_json"
    output_folder = tmp_path
    nome_file = "test"

    # ✅ Mock compatibile con headers e timeout
    def fake_requests_get(url, headers=None, timeout=20):
        class FakeResponse:
            status_code = 200
            def json(self): raise ValueError("JSON malformato")
            def raise_for_status(self): pass  # ✅ Metodo simulato
        return FakeResponse()

    import src.manifest_utils
    src.manifest_utils.requests.get = fake_requests_get

    manifest = download_manifest(manifest_url, output_folder, nome_file)
    assert manifest is None

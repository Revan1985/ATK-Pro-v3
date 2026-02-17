import pytest
import requests_mock
from src.image_downloader import download_info_json

@pytest.mark.parametrize("url,mock_json", [
    ("https://fake-url.com/data1.json", {"id": 1, "title": "mocked 1"}),
    ("https://fake-url.com/data2.json", {"id": 2, "title": "mocked 2"}),
    ("https://fake-url.com/data3.json", {"id": 3, "title": "mocked 3"}),
])
def test_download_info_json_varianti(url, mock_json):
    with requests_mock.Mocker() as m:
        m.get(url, json=mock_json)
        result = download_info_json(url)
        assert result == mock_json

def test_download_info_json_attivo():
    url = "https://fake-url.com/data.json"
    expected = {"id": 99}
    with requests_mock.Mocker() as m:
        m.get(url, json=expected)
        result = download_info_json(url)
        assert result == expected

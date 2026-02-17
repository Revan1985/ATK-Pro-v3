from src.canvas_id_extractor import extract_canvas_id_from_url

def test_extract_canvas_id_malformato():
    url = "http://example.com/senza_canvas_id"
    canvas_id = extract_canvas_id_from_url(url)
    assert canvas_id is None

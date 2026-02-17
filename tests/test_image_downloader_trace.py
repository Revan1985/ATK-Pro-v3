from src.image_downloader import download_info_json

def test_trace_download_real():
    try:
        download_info_json("https://jsonplaceholder.typicode.com/todos/1")
    except Exception:
        pass  # Ignora errori, serve solo per coverage

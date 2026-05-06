# File generato automaticamente il 2025-08-24 22:08:10
# Origine: ../../Archive/ATB_v1.4.1.exif_img_pdf_20250813/Antenati_Tile_Rebuilder_v1.4.1.py
# Modulo: image_downloader.py

# === Copertura test ===
# tests/test_image_downloader.py → download, gestione errori, salvataggio
# tests/test_image_downloader_parametrico.py → fallback e URL edge case
# tests/test_image_downloader_trace.py → logging e tracciamento interno
# ✅ Validato (logico) — test attivi e copertura 100%

# Librerie standard


# Librerie esterne
import requests

# Moduli interni


def download_info_json(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ),
        "Referer": "https://antenati.cultura.gov.it/"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()

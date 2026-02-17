# File generato automaticamente il 2025-08-24 22:08:10
# Origine: ../../Archive/ATB_v1.4.1.exif_img_pdf_20250813/Antenati_Tile_Rebuilder_v1.4.1.py
# Modulo: url_utils.py

# Librerie standard
import re

# Librerie esterne
# (nessuna in questo file)

# Moduli interni


def _parse_ua_from_url(url: str):
    # es. https://antenati.cultura.gov.it/ark:/12657/an_ua331277/Lor616G
    m = re.search(r'/ark:/12657/(an_[u][ad]\d+)', url)
    if m:
        return m.group(1)
    return None

def _parse_ark_from_url(url: str):
    m = re.search(r'/ark:/12657/([^/#\s]+(?:/[^#\s]+)?)', url)
    if m:
        return "ark:/12657/" + m.group(1)
    return None

def _last_segment(s: str):
    if not s:
        return None
    s = s.rstrip('/').split('/')[-1]
    return s or None

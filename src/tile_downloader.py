# -*- coding: utf-8 -*-
"""
tile_downloader.py — ATK-Pro v2.0 (adeguamento logica v1.4.1)
Scarica tutti i tiles IIIF di un canvas e restituisce la lista completa.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

HEADERS_UX = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://antenati.cultura.gov.it/",
    "Origin": "https://antenati.cultura.gov.it",
    "Connection": "keep-alive",
}

def download_tile(url, x, y, tile_size, output_dir):
    """Scarica un singolo tile IIIF e lo salva nella cartella di output."""
    # x,y possono arrivare come offset in pixel oppure come indici di col/row.
    # Se sono indici (es. 0,1) li moltiplichiamo per ottenere gli offset in pixel.
    if isinstance(x, int) and isinstance(y, int) and x < tile_size and y < tile_size:
        col = int(x)
        row = int(y)
        pixel_x = col * tile_size
        pixel_y = row * tile_size
    else:
        pixel_x = x
        pixel_y = y
        col = int(pixel_x // tile_size)
        row = int(pixel_y // tile_size)

    filename = os.path.join(output_dir, f"tile_{col}_{row}.jpg")
    url_tile = f"{url}/{pixel_x},{pixel_y},{tile_size},{tile_size}/full/0/default.jpg"

    # Tile già presente e valido
    if os.path.exists(filename) and os.path.getsize(filename) > 1024:
        logger.info("Tile già presente e valido: %s", filename)
        return filename

    # Ciclo di retry
    for attempt in range(1, MAX_RETRIES + 1):
        logger.info("[Tile] Scarico tile (tentativo %d/%d) da URL: %s", attempt, MAX_RETRIES, url_tile)
        try:
            response = requests.get(url_tile, headers=HEADERS_UX, stream=True, timeout=30)
        except Exception as e:
            logger.warning("Tentativo %d fallito per %s: %s", attempt, url_tile, e)
            continue

        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)
            # Controllo dimensione minima
            if os.path.getsize(filename) <= 1024:
                logger.warning("[Warning] Tile troppo piccolo: %s", filename)
                os.remove(filename)
                continue
            logger.info("[OK] Tile salvato correttamente: %s", filename)
            return filename
        elif response.status_code == 404:
            logger.debug("Tile non trovato (404): %s", url_tile)
            return None
        else:
            logger.error("[Error] Errore HTTP %s per %s", response.status_code, url_tile)
            continue

    logger.error("[Error] Tutti i tentativi di download falliti per %s", url_tile)
    return None

def download_tiles(infojson, output_dir, update_progress=None):
    """Scarica tutti i tile definiti in un info.json IIIF e restituisce la lista completa."""
    import concurrent.futures
    base_url = infojson["@id"]
    width = infojson["width"]
    height = infojson["height"]
    tile_w = infojson["tiles"][0]["width"]
    tile_h = infojson["tiles"][0].get("height", tile_w)  # tile rettangolari (AID §th)
    tile_size = tile_w  # mantenuto per compatibilità con download_tile()

    cols = (width + tile_w - 1) // tile_w
    rows = (height + tile_h - 1) // tile_h
    total = cols * rows
    logger.info("Inizio download di %d x %d tiles (tile_size=%d)", cols, rows, tile_size)
    os.makedirs(output_dir, exist_ok=True)

    def expected_tile_filename(x, y):
        col = int(x)
        row = int(y)
        return os.path.join(output_dir, f"tile_{col}_{row}.jpg")

    tile_args = [(base_url, x, y, tile_size, output_dir) for y in range(rows) for x in range(cols)]
    expected_files = [expected_tile_filename(x, y) for y in range(rows) for x in range(cols)]

    max_global_retries = 3
    # Parallelizzazione automatica: usa metà dei core disponibili, minimo 2, massimo 8
    try:
        cpu_count = os.cpu_count() or 4
        max_workers = min(8, max(2, cpu_count // 2))
    except Exception:
        max_workers = 4
    attempt = 0
    tiles_downloaded = set()
    missing_files = set(expected_files)
    done = 0

    while attempt < max_global_retries and missing_files:
        logger.info(f"[Tiles] Tentativo globale {attempt+1}/{max_global_retries}. Tiles da scaricare: {len(missing_files)}")
        args_to_download = []
        for idx, (x, y) in enumerate([(x, y) for y in range(rows) for x in range(cols)]):
            fname = expected_tile_filename(x, y)
            if fname in missing_files:
                args_to_download.append((base_url, x, y, tile_size, output_dir))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_tile = {executor.submit(download_tile, *args): args for args in args_to_download}
            for future in concurrent.futures.as_completed(future_to_tile):
                result = future.result()
                done += 1
                if result:
                    tiles_downloaded.add(result)
                    missing_files.discard(result)
                if update_progress:
                    try:
                        progress = min(1.0, max(0.0, done / float(total * max_global_retries)))
                        update_progress(progress)
                    except Exception:
                        pass
        # Dopo ogni ciclo, aggiorna missing_files
        missing_files = set(f for f in expected_files if not (os.path.exists(f) and os.path.getsize(f) > 1024))
        attempt += 1

    if missing_files:
        logger.warning(f"[Tiles] ATTENZIONE: {len(missing_files)} tile NON scaricati dopo {max_global_retries} tentativi.")
        for mf in sorted(missing_files):
            logger.warning(f"[Tiles] Mancante: {mf}")
    else:
        logger.info("[Tiles] Tutti i tile scaricati correttamente.")

    logger.info("[Tiles] Download completato di %d/%d scaricati", len(tiles_downloaded), total)
    return list(tiles_downloaded), list(missing_files)

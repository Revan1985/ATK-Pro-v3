# -*- coding: utf-8 -*-
# Modulo: input_parser.py
# Parsing file di input (modalità + URL)
# Riallineato alla logica Antenati_Tile_Rebuilder_v1.4.1.py

import logging

logger = logging.getLogger(__name__)

def parse_input_text(testo):
    """
    Parsing del testo di input:
    - Ignora righe vuote e commenti (#)
    - Processa le righe a coppie: modalità + URL
    - Normalizza la modalità (D/R)
    - Valida gli URL (solo http/https)
    - Normalizza il vecchio dominio www.antenati.san.beniculturali.it → antenati.cultura.gov.it
    - Restituisce lista di dict con modalita, nome_file, url
    """
    righe = testo.strip().splitlines()
    risultati = []

    # Pulizia e filtraggio righe
    righe = [riga.strip() for riga in righe if riga.strip() and not riga.strip().startswith("#")]

    # Processa le righe a coppie
    for i in range(0, len(righe) - 1, 2):
        riga_modalita = righe[i]
        riga_url = righe[i + 1].strip()

        # Salta se l’URL è vuoto o non valido
        if not riga_url.startswith("http"):
            logger.warning(f"⚠️ URL non valido: {riga_url}")
            continue
        # Normalizza URL vecchio dominio → nuovo dominio
        if "www.antenati.san.beniculturali.it" in riga_url:
            riga_url_orig = riga_url
            riga_url = riga_url.replace("www.antenati.san.beniculturali.it", "antenati.cultura.gov.it")
            logger.info(f"🔄 URL normalizzato: {riga_url_orig} → {riga_url}")

        # Intercetta URL detail-nominative → risolvi all'ARK an_ud corrispondente
        if "detail-nominative" in riga_url:
            import requests as _req
            logger.info(f"🔍 detail-nominative rilevato, risolvo ARK da: {riga_url}")
            try:
                _headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://antenati.cultura.gov.it/"
                }
                _resp = _req.get(riga_url, headers=_headers, timeout=10)
                _resp.raise_for_status()
                import re as _re
                # Cerca il primo ARK an_ud (unità documentale = registro)
                _match = _re.search(r'/ark:/12657/(an_ud[A-Za-z0-9]+)', _resp.text)
                if _match:
                    riga_url_orig = riga_url
                    riga_url = f"https://antenati.cultura.gov.it/ark:/12657/{_match.group(1)}"
                    logger.info(f"🔄 detail-nominative → {riga_url}")
                else:
                    logger.warning(f"⚠️ detail-nominative: nessun ARK trovato in {riga_url}")
            except Exception as _e:
                logger.warning(f"⚠️ detail-nominative: errore risoluzione ({_e}), URL invariato")
        # Estrai modalità e nome file
        if "-" in riga_modalita:
            parti = riga_modalita.split("-", 1)
            modalita_raw = parti[0].strip()
            nome_file = parti[1].strip()
        else:
            modalita_raw = riga_modalita.strip()
            nome_file = "Senza nome"

        # Normalizza modalità
        modalita = modalita_raw.upper()
        if modalita not in ["D", "R"]:
            logger.warning(f"⚠️ Modalità non riconosciuta: {modalita_raw}")
            continue

        # Rileva se l'URL è direttamente un manifest IIIF (es. termina con /manifest.json o /manifest)
        url_stripped = riga_url.split("?")[0].rstrip("/")
        manifest_direct = url_stripped.endswith("/manifest.json") or url_stripped.endswith("/manifest")

        risultati.append({
            "modalita": modalita,
            "nome_file": nome_file,
            "url": riga_url,
            "manifest_direct": manifest_direct,
        })

    return risultati

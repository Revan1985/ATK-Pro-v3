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

        risultati.append({
            "modalita": modalita,
            "nome_file": nome_file,
            "url": riga_url
        })

    return risultati

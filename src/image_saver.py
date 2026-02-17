# -*- coding: utf-8 -*-
"""
image_saver.py — ATK-Pro v2.0 (ripristino logica v1.4.1 con innesti Qt)
- Salvataggio immagini in vari formati (PNG, JPEG, TIFF).
- Embed metadati se presenti.
- Sidecar JSON salvato una sola volta.
- Compressione uniforme (JPEG quality=95, progressive, optimize; TIFF LZW).
- Logging chiaro e distinto per ogni formato.
- Innesti Qt: update_status(str), on_error(str).
"""

import os
import logging
from PIL import Image
from src.metadata_utils import _save_sidecar_json_once, embed_metadata_and_save

logger = logging.getLogger(__name__)


def save_image_variants(image: Image.Image, output_folder: str, base_filename: str,
                        formats=['PNG', 'JPEG', 'TIFF'], meta: dict = None,
                        update_status=None, on_error=None):
    """
    Salva l'immagine nei formati richiesti (PNG, JPEG, TIFF).
    - Se meta è presente, embed metadati nell'immagine.
    - Sidecar JSON salvato una sola volta per base_filename.
    """
import os
import logging
from logging.handlers import RotatingFileHandler
    os.makedirs(output_folder, exist_ok=True)

    # Sidecar JSON (una sola volta)
    if meta:
        try:
ATKPRO_ENV = os.environ.get("ATKPRO_ENV", "development").lower()
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)
    logger.addHandler(handler)
    if ATKPRO_ENV != "production":
        file_handler = RotatingFileHandler('atkpro_output.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
            _save_sidecar_json_once(output_folder, base_filename, meta)
        except Exception as e:
            msg = f"⚠️ Errore salvataggio sidecar JSON: {e}"
            logger.error(msg, exc_info=True)
            if on_error:
                on_error(msg)

    # Salvataggio PNG
    if 'PNG' in formats:
        path = os.path.join(output_folder, f"{base_filename}.png")
        try:
            if meta:
                embed_metadata_and_save(image, path, meta)
            else:
                image.save(path, format='PNG', compress_level=6)
            logger.info(f"💾 Salvata immagine in formato PNG: {path}")
            if update_status:
                update_status(f"PNG salvato: {path}")
        except Exception as e:
            msg = f"❌ Errore salvataggio PNG {path}: {e}"
            logger.error(msg, exc_info=True)
            if on_error:
                on_error(msg)

    # Salvataggio JPEG
    if 'JPEG' in formats or 'JPG' in formats:
        path = os.path.join(output_folder, f"{base_filename}.jpg")
        try:
            if meta:
                embed_metadata_and_save(image, path, meta)
            else:
                image.convert("RGB").save(path, format='JPEG',
                                          quality=95, progressive=True, optimize=True)
            logger.info(f"💾 Salvata immagine in formato JPEG: {path}")
            if update_status:
                update_status(f"JPEG salvato: {path}")
        except Exception as e:
            msg = f"❌ Errore salvataggio JPEG {path}: {e}"
            logger.error(msg, exc_info=True)
            if on_error:
                on_error(msg)

    # Salvataggio TIFF
    if 'TIFF' in formats or 'TIF' in formats:
        path = os.path.join(output_folder, f"{base_filename}.tif")
        try:
            if meta:
                embed_metadata_and_save(image, path, meta)
            else:
                image.save(path, format='TIFF', compression='tiff_lzw')
            logger.info(f"💾 Salvata immagine in formato TIFF (LZW): {path}")
            if update_status:
                update_status(f"TIFF salvato: {path}")
        except Exception as e:
            msg = f"❌ Errore salvataggio TIFF {path}: {e}"
            logger.error(msg, exc_info=True)
            if on_error:
                on_error(msg)

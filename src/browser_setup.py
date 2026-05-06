# -*- coding: utf-8 -*-
# Modulo: browser_setup.py
# Setup Selenium e Playwright per il caricamento delle pagine
# Riallineato alla logica Antenati_Tile_Rebuilder_v1.4.1.py

import os
import sys
import logging

logger = logging.getLogger(__name__)

# Imposta il path locale per i browser Playwright inclusi nel bundle EXE
if getattr(sys, 'frozen', False):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(sys._MEIPASS, "ms-playwright")

# === Selenium Setup ===
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def setup_selenium():
    """
    Avvia Selenium con Chrome headless e ritorna il driver,
    oppure None se fallisce.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service()
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("[OK] Selenium avviato correttamente.")
        return driver
    except Exception as e:
        logger.error(f"[Selenium] Errore: {e}", exc_info=True)
        return None

# === Playwright Setup ===
from playwright.sync_api import sync_playwright

def setup_playwright(url):
    """
    Avvia Playwright con Chromium headless, carica la pagina e ritorna l'HTML,
    oppure None se fallisce.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=15000)  # 15 secondi di timeout
            page.wait_for_timeout(5000)    # attesa per caricamento dinamico
            html = page.content()
            browser.close()
            logger.info("[OK] Playwright ha caricato la pagina correttamente.")
            return html
    except Exception as e:
        logger.error(f"Errore in setup_playwright: {e}", exc_info=True)
        return None


def fetch_manifest_json_via_playwright(url: str) -> dict | None:
    """
    Scarica un manifest IIIF JSON usando Playwright (page.goto + response.body).
    Bypassa il TLS fingerprinting dei portali che bloccano Python/urllib3
    (es. Gallica BnF) perché usa il TLS stack completo di Chromium.
    """
    import json as _json
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                extra_http_headers={
                    "Accept": "application/ld+json, application/json, */*",
                }
            )
            page = context.new_page()
            # page.goto usa il TLS Chromium completo (non Node.js HTTP)
            response = page.goto(url, timeout=25000, wait_until="networkidle")
            if response and response.ok:
                body = response.body()
                data = _json.loads(body)
                browser.close()
                logger.info(f"[OK] Playwright fetch manifest ({response.status}): {url}")
                return data
            status = response.status if response else "N/A"
            logger.warning(f"[Playwright] fetch manifest status {status} per {url}")
            browser.close()
            return None
    except Exception as e:
        logger.error(f"[Playwright] fetch_manifest_json_via_playwright fallito: {e}", exc_info=True)
        return None

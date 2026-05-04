import requests
import re
import logging
import os
import json
from logging.handlers import RotatingFileHandler
import time
ATKPRO_ENV = os.environ.get("ATKPRO_ENV", "development").lower()
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)
    logger.addHandler(handler)
    if ATKPRO_ENV != "production":
        file_handler = RotatingFileHandler('atkpro_output.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)

# Pacchetto di chiavi HTTP "umane", ripreso integralmente dalla v1.4.1
HEADERS_UX = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://antenati.cultura.gov.it/",
    "Origin": "https://antenati.cultura.gov.it",
    "Connection": "keep-alive",
}

# Regex permissive v1.4.1 per intercettare il manifest nel DOM/HTML
_RE_MANIFEST_ANY = re.compile(
    r"https://dam-antenati\.cultura\.gov\.it/antenati/containers/[A-Za-z0-9]+/manifest"
)
# Supporto anche a varianti accidentalmente espanse
_RE_MANIFEST_JSON = re.compile(
    r"https://dam-antenati\.cultura\.gov\.it/antenati/containers/[A-Za-z0-9]+/manifest\.json"
)

def _find_manifest_in_html(html: str) -> str | None:
    """
    Cerca il manifest direttamente nell'HTML, replicando la logica v1.4.1.
    """
    if not html:
        return None
    # Preferiamo link che includono esplicitamente '.json' se presenti
    m = _RE_MANIFEST_JSON.search(html)
    if m:
        manifest_url = m.group(0)
        print(f"[Manifest] Trovato: {manifest_url}")
        return manifest_url
    # Poi la variante v1.4.1 classica (containers/.../manifest)
    m = _RE_MANIFEST_ANY.search(html)
    if m:
        manifest_url = m.group(0)
        print(f"[Manifest] Trovato: {manifest_url}")
        return manifest_url
    # Accetta anche link relativi come href="manifest.json" o "/manifest.json"
    m = re.search(r'href=[\"\']([^\"\']*manifest(?:\.json)?)[\"\']', html, re.IGNORECASE)
    if m:
        manifest_url = m.group(1)
        print(f"[Manifest] Trovato (relativo): {manifest_url}")
        return manifest_url
    return None

def _http_get(url: str, timeout: int = 20) -> requests.Response | None:
    """
    GET con HEADERS_UX completi (v1.4.1), indispensabili per 'aprire' il portale.
    """
    try:
        r = requests.get(url, headers=HEADERS_UX, timeout=timeout)
        logger.debug(f"GET {url} -> {r.status_code}")
        return r
    except Exception as e:
        logger.warning(f"[HTTP] Errore GET {url}: {e}")
        return None


# ──────────────────────────────────────────────────────────────────
# Builder URL manifest per portali IIIF supportati (Layer 1)
# ──────────────────────────────────────────────────────────────────

def _build_gallica_manifest(page_url: str) -> str | None:
    """Gallica BnF: .../ark:/12148/{id} → .../iiif/ark:/12148/{id}/manifest.json"""
    m = re.search(r'gallica\.bnf\.fr(.*/ark:/12148/[A-Za-z0-9]+)', page_url)
    if m:
        return f"https://gallica.bnf.fr/iiif{m.group(1)}/manifest.json"
    return None


def _build_ia_manifest(page_url: str) -> str | None:
    """Internet Archive: archive.org/details/{id} → iiif.archivelab.org/iiif/{id}/manifest.json"""
    m = re.search(r'archive\.org/details/([A-Za-z0-9._-]+)', page_url)
    if m:
        return f"https://iiif.archivelab.org/iiif/{m.group(1)}/manifest.json"
    return None


def _build_ecodices_manifest(page_url: str) -> str | None:
    """e-codices: sia /en/{lib}/{id}/ che /list/one/{lib}/{id} → .../metadata/iiif/{lib}-{id}/manifest.json"""
    # Formato viewer: /en/csg/0390/1r/max  oppure  /list/one/csg/0390
    m = re.search(
        r'e-codices\.unifr\.ch/(?:[a-z]+/[a-z]+/one/|[a-z]{2}/)([A-Za-z0-9]+)/([A-Za-z0-9-]+)',
        page_url
    )
    if m:
        doc_id = f"{m.group(1)}-{m.group(2)}"
        return f"https://www.e-codices.unifr.ch/metadata/iiif/{doc_id}/manifest.json"
    return None


def _build_heidelberg_manifest(page_url: str) -> str | None:
    """Heidelberg UB: .../diglit/{id} → .../diglit/iiif/{id}/manifest.json (IIIF v2)"""
    m = re.search(r'digi\.ub\.uni-heidelberg\.de/diglit/(?:iiif/)?([A-Za-z0-9_.-]+)', page_url)
    if m:
        doc_id = m.group(1)
        return f"https://digi.ub.uni-heidelberg.de/diglit/iiif/{doc_id}/manifest.json"
    return None


# Mappa portale → funzione builder
_PORTAL_BUILDERS = {
    "gallica":          _build_gallica_manifest,
    "internet_archive": _build_ia_manifest,
    "e_codices":        _build_ecodices_manifest,
    "heidelberg":       _build_heidelberg_manifest,
}


def resolve_manifest_url(page_url: str, portale: str) -> str | None:
    """
    Costruisce direttamente l'URL del manifest IIIF partendo dall'URL di pagina,
    usando la logica specifica del portale.

    - "manifest_diretto": l'URL è già il manifest, restituisce page_url invariato.
    - "gallica", "internet_archive", "e_codices", "heidelberg": costruisce URL manifest.
    - "antenati", "bodleian" (e altri): restituisce None → il chiamante usa
      Selenium/Playwright + scraping HTML (percorso legacy).
    """
    portale_key = portale.lower().replace("-", "_").replace(" ", "_")
    if portale_key == "manifest_diretto":
        return page_url
    builder = _PORTAL_BUILDERS.get(portale_key)
    if builder:
        return builder(page_url)
    return None

def find_manifest_url(driver) -> str | None:
    """
    Compatibilità v1.4.1: legge il DOM da Selenium e cerca containers/.../manifest.
    Riprende sleep e messaggi identici per allineare i log.
    """
    time.sleep(3)
    print("[Manifest] Cerco manifest nell'HTML...")
    try:
        html = driver.page_source
    except Exception as e:
        logger.warning(f"[Manifest] Impossibile leggere page_source: {e}")
        html = ""
    manifest_url = _find_manifest_in_html(html)
    if not manifest_url:
        print("[Manifest] Nessun manifest trovato nell'HTML.")
    return manifest_url

def robust_find_manifest(page_url: str, html: str | None = None) -> str | None:
    """
    Ricerca robusta del manifest quando si parte dall'URL della pagina.
    - Se viene passato html, prova subito il parsing v1.4.1.
    - Altrimenti scarica l'HTML con HEADERS_UX e cerca i link containers/.../manifest.
    - Prova anche varianti con slash finale.
    - Come ultimo tentativo, parse di script JSON/Mirador che contengono 'manifest'.
    """
    # 1) Se abbiamo già HTML, prova subito
    if html:
        print("[Manifest] Cerco nell'HTML...")
        m = _find_manifest_in_html(html)
        if m:
            return m
        print("[Manifest] Nessun manifest trovato nell'HTML.")

    # 2) Scarica l'HTML della pagina come browser reale (HEADERS_UX)
    print("[Manifest] Scarico HTML della pagina...")
    r = _http_get(page_url, timeout=25)
    if r and r.ok:
        text = r.text or ""
        # Parsing diretto (v1.4.1)
        print("[Manifest] Cerco nell'HTML...")
        m = _find_manifest_in_html(text)
        if m:
            return m

        # 3) Varianti con slash finale o link indiretti
        if page_url.endswith("/"):
            alt_url = page_url[:-1]
        else:
            alt_url = page_url + "/"
        if alt_url != page_url:
            print("[Manifest] Provo variante URL...")
            r2 = _http_get(alt_url, timeout=20)
            if r2 and r2.ok:
                m2 = _find_manifest_in_html(r2.text or "")
                if m2:
                    print("[Manifest] Trovato via slash finale.")
                    return m2

        # 4) Parsing di script Mirador/JSON inline (casi in cui 'manifest' appare in oggetti)
        print("[Manifest] Cerco in script/JSON inline...")
        # Cerca 'manifest' come chiave o valore di oggetti json embed
        m3 = re.search(
            r'"manifest"\s*:\s*"(https://dam-antenati\.cultura\.gov\.it/antenati/containers/[A-Za-z0-9]+/manifest(?:\.json)?)"',
            text
        )
        if m3:
            manifest_url = m3.group(1)
            print(f"[Manifest] Trovato: {manifest_url}")
            return manifest_url

    # 5) Nessun manifest trovato
    print("[Manifest] Nessun manifest trovato.")
    return None

def download_manifest(manifest_url: str, output_folder: str, titolo_doc: str = "documento", referer: str | None = None) -> dict | None:
    """
    Scarica il manifest replicando la logica v1.4.1:
    - HEADERS_UX completi (User-Agent, Accept, Referer, Origin, Accept-Language, Connection)
    - Gestione esplicita di 403 e 5xx
    - Salvataggio su disco con nome identico alla v1.4.1
    - Messaggi di log identici per verifica bit-a-bit
    - referer: se fornito, sovrascrive Referer/Origin negli header (per portali non-Antenati)
    """
    print(f"[Manifest] Download da: {manifest_url}")
    # Adatta gli header al portale: usa referer specificato o default Antenati
    headers = dict(HEADERS_UX)
    if referer:
        headers["Referer"] = referer.rstrip("/") + "/"
        headers["Origin"] = referer.rstrip("/")
    max_retries = 3
    delay = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(manifest_url, headers=headers, timeout=25)

            # Log codici utili
            if response is None:
                print(f"[Manifest] Tentativo {attempt}: Nessuna risposta")
            else:
                print(f"[Manifest] Tentativo {attempt}: codice {response.status_code}")

            if response is None:
                raise requests.exceptions.RequestException("Nessuna risposta")

            if response.status_code == 403:
                print("[Manifest] Accesso negato (403).")
                return None

            # In caso di errori server (5xx) proviamo un retry
            if response.status_code >= 500:
                print(f"[Manifest] Errore server ({response.status_code}) al tentativo {attempt}.")
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    return None

            response.raise_for_status()
            try:
                manifest = response.json()
            except Exception as e:
                # Manifest non decodificabile (corrotto): log e fallback
                print(f"[Manifest] Contenuto manifest non decodificabile: {e}")
                return None

            os.makedirs(output_folder, exist_ok=True)

            # Estrai ID contenitore dall'URL (identico alla v1.4.1)
            container_id = manifest_url.strip("/").split("/")[-2]
            titolo_pulito = re.sub(r'[\\/*?:"<>|]', "", titolo_doc).replace(" ", "_")
            manifest_filename = f"manifest_{container_id}_{titolo_pulito}.json"
            manifest_path = os.path.join(output_folder, manifest_filename)

            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)

            print(f"[Manifest] Salvato in: {manifest_path}")
            return manifest

        except requests.exceptions.RequestException as e:
            print(f"[Manifest] Tentativo {attempt} fallito: {e}")
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            else:
                print(f"[Manifest] Errore download definitivo dopo {max_retries} tentativi")
                return None

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
    """Internet Archive: restituisce un placeholder URL riconoscibile; il manifest
    sintetico viene costruito da build_ia_synthetic_manifest() in elaborazione."""
    m = re.search(r'archive\.org/(?:details|stream|download)/([A-Za-z0-9._-]+)', page_url)
    if m:
        return f"https://iiif.archivelab.org/iiif/{m.group(1)}/manifest.json"
    return None


def build_ia_synthetic_manifest(page_url: str) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico per un item di Internet Archive usando:
      - archive.org/metadata/{item_id}  → server, dir, file list
      - {server}{dir}/{item_id}_page_numbers.json → conteggio pagine
      - BookReaderImages.php  → URL immagine per ogni pagina

    Il manifest prodotto usa 'ia_direct' come contesto del service, riconoscibile
    da download_ia_page() in elaborazione.py per il download diretto senza tile.
    """
    m = re.search(r'archive\.org/(?:details|stream|download)/([A-Za-z0-9._-]+)', page_url)
    if not m:
        logger.error(f"[IA] URL non riconoscibile: {page_url}")
        return None
    item_id = m.group(1)

    try:
        _h = dict(HEADERS_UX)
        meta_r = requests.get(f'https://archive.org/metadata/{item_id}', headers=_h, timeout=15)
        meta_r.raise_for_status()
        data = meta_r.json()
    except Exception as e:
        logger.error(f"[IA] Metadata API fallita per {item_id}: {e}")
        return None

    server = data.get('server', '')
    dir_ = data.get('dir', '')
    files = data.get('files', [])
    item_meta = data.get('metadata', {})

    if not server or not dir_:
        logger.error(f"[IA] Metadati incompleti per {item_id}: server={server!r} dir={dir_!r}")
        return None

    # Trova JP2 ZIP (non-raw, primo disponibile)
    jp2_zip = next(
        (f for f in files
         if f.get('name', '').endswith('_jp2.zip') and 'raw' not in f.get('name', '')),
        None
    )
    if not jp2_zip:
        logger.error(f"[IA] Nessun JP2 ZIP trovato per {item_id}")
        return None

    zip_name = jp2_zip['name'].replace('_jp2.zip', '')
    zip_path = dir_ + '/' + jp2_zip['name']

    # Conta le pagine tramite page_numbers.json
    pn_file = next((f for f in files if f.get('name', '').endswith('_page_numbers.json')), None)
    num_pages = 0
    if pn_file:
        try:
            pn_r = requests.get(
                f'https://{server}{dir_}/{pn_file["name"]}', headers=_h, timeout=12
            )
            if pn_r.ok:
                num_pages = len(pn_r.json().get('pages', []))
        except Exception as e:
            logger.warning(f"[IA] page_numbers.json non disponibile: {e}")

    if num_pages == 0:
        logger.error(f"[IA] Impossibile determinare numero pagine per {item_id}")
        return None

    title = item_meta.get('title', item_id)
    if isinstance(title, list):
        title = title[0]

    def _make_ia_canvas(page_num: int) -> dict:
        page_file = f'{zip_name}_jp2/{zip_name}_{str(page_num).zfill(4)}.jp2'
        img_url = (
            f'https://{server}/BookReader/BookReaderImages.php'
            f'?zip={zip_path}&file={page_file}&id={item_id}&scale=1&rotate=0'
        )
        return {
            '@id': f'https://archive.org/bookreader/{item_id}/canvas/{page_num}',
            '@type': 'sc:Canvas',
            'label': f'Page {page_num}',
            'width': 800,
            'height': 1200,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': img_url,
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'ia_direct',
                        '@id': img_url,
                        'profile': 'ia_direct'
                    }
                }
            }]
        }

    canvases = [_make_ia_canvas(i) for i in range(1, num_pages + 1)]
    logger.info(f"[IA] Manifest sintetico costruito: {item_id}, {num_pages} pagine")

    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f'https://archive.org/details/{item_id}',
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@type': 'sc:Sequence',
            'canvases': canvases
        }]
    }


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


def _build_memooria_manifest(page_url: str) -> str | None:
    """Memooria/Jarvis (qualsiasi biblioteca):
    - URL legacy:  .../schedadl.aspx?id={guid}
    - URL nuovo COOSMO: .../catalog/{collUuid}/cultural-item/{guid}
    → https://{subdomain}.jarvis.memooria.org/meta/iiif/{guid}/manifest (IIIF v2/v3)
    """
    # Estrae il hostname (es. brixiana.jarvis.memooria.org, parma.jarvis.memooria.org)
    host_m = re.search(r'https?://([^/]+\.jarvis\.memooria\.org)', page_url, re.IGNORECASE)
    _guid_pat = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    # Formato COOSMO nuovo: /cultural-item/{guid}
    coosmo_m = re.search(r'/cultural-item/' + _guid_pat, page_url, re.IGNORECASE)
    # Formato legacy Jarvis: ?id={guid}
    legacy_m = re.search(r'[?&]id=' + _guid_pat, page_url, re.IGNORECASE)
    guid_m = coosmo_m or legacy_m
    if host_m and guid_m:
        host = host_m.group(1).lower()
        guid = guid_m.group(1).lower()
        return f"https://{host}/meta/iiif/{guid}/manifest"
    # Fallback: nessun hostname esplicito ma GUID presente
    if guid_m:
        guid = guid_m.group(1).lower()
        return f"https://brixiana.jarvis.memooria.org/meta/iiif/{guid}/manifest"
    return None

# Alias per compatibilità con portale "brixiana" già configurato
_build_brixiana_manifest = _build_memooria_manifest


def _build_findbuch_manifest(page_url: str) -> str | None:
    """findbuch.net: *.findbuch.net/php/view.php?link={hex}
    Supporta: kirchenbücher-südtirol.findbuch.net e tutti i subdomain findbuch.net
    Restituisce l'URL della pagina come placeholder (elaborato da build_findbuch_synthetic_manifest).
    """
    if re.search(r'findbuch\.net/php/view\.php', page_url, re.IGNORECASE):
        return page_url
    return None


def build_findbuch_synthetic_manifest(page_url: str) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico per un registro findbuch.net.
    Scarica l'HTML del viewer e ne estrae be_id, ve_id e il numero di immagini.
    Il download avviene via gtpc.php con una sessione PHP attivata da main.php+view.php.
    """
    # Ricava base URL (es. https://www.kirchenbücher-südtirol.findbuch.net/php/)
    from urllib.parse import urlparse
    parsed = urlparse(page_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}/php/"

    try:
        _h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        # Attiva la sessione PHP visitando main.php prima di view.php
        _sess = requests.Session()
        _sess.get(base_url + 'main.php', headers=_h, timeout=15)
        r = _sess.get(page_url, headers={**_h, 'Referer': base_url + 'main.php'}, timeout=20)
        r.raise_for_status()
        r.encoding = 'utf-8'
        html = r.text
    except Exception as e:
        logger.error(f"[Findbuch] Errore fetch pagina {page_url}: {e}")
        return None

    # Estrai be_id e ve_id dal JS inline della pagina viewer
    be_id_m  = re.search(r'var\s+be_id\s*=\s*(\d+)', html)
    ve_id_m  = re.search(r"var\s+ve_id\s*=\s*['\"]?(\d+)['\"]?", html)
    max_m    = re.search(r'var\s+max\s*=\s*(\d+)', html)
    if not be_id_m or not ve_id_m:
        logger.error(f"[Findbuch] be_id/ve_id non trovati in {page_url}")
        return None

    be_id  = int(be_id_m.group(1))
    ve_id  = int(ve_id_m.group(1))
    n_imgs = int(max_m.group(1)) if max_m else 0

    # Estrai pic_names per le label (opzionale, fallback a "Pagina N")
    pic_names = re.findall(r"pic_names\[\d+\]\s*=\s*'([^']+)'", html)

    if n_imgs == 0:
        logger.error(f"[Findbuch] max=0 immagini in {page_url}")
        return None

    # Estrai titolo dall'HTML
    bestand_m = re.search(r'<b>Bestand:</b></div>\s*<div[^>]*>([^<]+)</div>', html)
    titel_m   = re.search(r'<b>Titel:</b></div>\s*<div[^>]*>([^<]+)</div>', html)
    if titel_m and bestand_m:
        title = f"{bestand_m.group(1).strip()} – {titel_m.group(1).strip()}"
    elif bestand_m:
        title = bestand_m.group(1).strip()
    elif titel_m:
        title = titel_m.group(1).strip()
    else:
        title = "Registro findbuch"

    link_m = re.search(r'[?&]link=([A-Za-z0-9]+)', page_url)
    link_id = link_m.group(1) if link_m else "unknown"

    def _make_canvas(idx: int) -> dict:
        label = pic_names[idx] if idx < len(pic_names) else f"Pagina {idx + 1}"
        return {
            '@id': f"synthetic://findbuch/{link_id}/canvas/{idx}",
            '@type': 'sc:Canvas',
            'label': label,
            'width': 1000,
            'height': 1400,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': f"gtpc://findbuch/{be_id}/{ve_id}/{idx}",
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'findbuch_gtpc',
                        '@id': f"gtpc://findbuch/{be_id}/{ve_id}/{idx}",
                        'be_id': be_id,
                        've_id': ve_id,
                        'count': idx,
                        'view_url': page_url,
                        'base_url': base_url,
                    }
                }
            }]
        }

    canvases = [_make_canvas(i) for i in range(n_imgs)]
    logger.info(f"[Findbuch] Manifest sintetico: '{title}', {n_imgs} immagini (be_id={be_id}, ve_id={ve_id})")

    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f"synthetic://findbuch/{link_id}",
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@id': f"synthetic://findbuch/{link_id}/sequence/1",
            '@type': 'sc:Sequence',
            'canvases': canvases
        }]
    }


def _build_matricula_manifest(page_url: str) -> str | None:
    """Matricula Online: https://data.matricula-online.eu/de/{nazione}/{diocesi}/{parrocchia}/{libro}/
    Restituisce l'URL della pagina come placeholder (elaborato da build_matricula_synthetic_manifest).
    """
    if re.search(r'data\.matricula-online\.eu/', page_url, re.IGNORECASE):
        return page_url
    return None


def build_matricula_synthetic_manifest(page_url: str, html: str | None = None) -> dict | None:
    """
    Costruisce un manifest IIIF sintetico per un registro Matricula Online.
    Estrae i /image/base64url dal viewer JS MatriculaDocView, decodifica ogni
    URL JPEG e costruisce il manifest.

    Se html è fornito (es. già ottenuto via Selenium), viene usato direttamente
    senza un secondo fetch HTTP (che fallirebbe con 503 bot-blocker).
    Le immagini usano service['@context'] = 'matricula_direct' per essere
    riconosciute da elaborazione.py (nessun header speciale richiesto).
    """
    import base64 as _b64
    if html is None:
        try:
            _h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(page_url, headers=_h, timeout=20)
            r.raise_for_status()
            r.encoding = 'utf-8'
            html = r.text
        except Exception as e:
            logger.error(f"[Matricula] Errore fetch pagina {page_url}: {e}")
            return None

    # Estrai URL immagini codificate base64 dal viewer MatriculaDocView
    encoded_imgs = re.findall(r'"/image/([A-Za-z0-9+/=]{20,})"', html)
    if not encoded_imgs:
        logger.error(f"[Matricula] Nessuna immagine trovata in {page_url}")
        return None

    # Decodifica ogni URL base64 → URL JPEG su hosted-images.matricula-online.eu
    img_urls = []
    for enc in encoded_imgs:
        try:
            padded = enc + '=' * (-len(enc) % 4)
            decoded = re.sub(r'[\x00-\x1f\x7f]', '', _b64.b64decode(padded).decode('utf-8')).rstrip('/?')
            decoded = decoded.replace('http://', 'https://', 1)  # forza HTTPS
            img_urls.append(decoded)
        except Exception:
            continue

    if not img_urls:
        logger.error(f"[Matricula] Nessuna URL decodificabile in {page_url}")
        return None

    # Etichette pagina dall'array "labels"
    labels_m = re.search(r'"labels":\s*\[([^\]]+)\]', html)
    if labels_m:
        labels = re.findall(r'"([^"]+)"', labels_m.group(1))
    else:
        labels = [f"Pagina {i + 1}" for i in range(len(img_urls))]

    # Titolo dal <title>: "Taufbuch - 01-001 | Parrocchia | Diocesi | Matricula Online"
    title_m = re.search(r'<title>([^<]+)</title>', html)
    title = title_m.group(1).strip() if title_m else "Registro Matricula"
    if ' | Matricula' in title:
        title = title[:title.index(' | Matricula')]

    # ID univoco dall'URL (es. "oesterreich/wien/01-st-stephan/01-001")
    mat_id = re.sub(r'https?://data\.matricula-online\.eu/[a-z]{2}/', '', page_url).strip('/')

    def _make_canvas(idx: int, img_url: str, label: str) -> dict:
        return {
            '@id': f"synthetic://matricula/{mat_id}/canvas/{idx}",
            '@type': 'sc:Canvas',
            'label': label,
            'width': 1000,
            'height': 1400,
            'images': [{
                '@type': 'oa:Annotation',
                'motivation': 'sc:painting',
                'resource': {
                    '@type': 'dctypes:Image',
                    '@id': img_url,
                    'format': 'image/jpeg',
                    'service': {
                        '@context': 'matricula_direct',
                        '@id': img_url,
                        'profile': 'matricula_direct'
                    }
                }
            }]
        }

    canvases = [
        _make_canvas(i, u, labels[i] if i < len(labels) else f"Pagina {i + 1}")
        for i, u in enumerate(img_urls)
    ]
    logger.info(f"[Matricula] Manifest sintetico: '{title}', {len(img_urls)} immagini")

    return {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f"synthetic://matricula/{mat_id}",
        '@type': 'sc:Manifest',
        'label': title,
        'sequences': [{
            '@id': f"synthetic://matricula/{mat_id}/sequence/1",
            '@type': 'sc:Sequence',
            'canvases': canvases
        }]
    }


# Mappa portale → funzione builder
_PORTAL_BUILDERS = {
    "gallica":          _build_gallica_manifest,
    "internet_archive": _build_ia_manifest,
    "e_codices":        _build_ecodices_manifest,
    "heidelberg":       _build_heidelberg_manifest,
    "brixiana":         _build_memooria_manifest,
    "memooria":         _build_memooria_manifest,
    "findbuch":         _build_findbuch_manifest,
    "matricula":        _build_matricula_manifest,
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

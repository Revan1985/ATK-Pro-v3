# -*- coding: utf-8 -*-
"""
test_portals.py — Verifica rapida manifest IIIF per tutti i portali supportati.
Scarica solo il manifest (+ info.json del primo canvas) senza scaricare tile.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json
import time
from manifest_utils import resolve_manifest_url, download_manifest, build_ia_synthetic_manifest

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, */*",
}

TEST_CASES = [
    {
        "portale": "internet_archive",
        "label": "Internet Archive",
        "url": "https://archive.org/details/birdbookillustra00reedrich",
        "ia_synthetic": True,
    },
    {
        "portale": "e_codices",
        "label": "e-codices (Codex Sangallensis 390)",
        "url": "https://www.e-codices.unifr.ch/en/csg/0390/1r/max",
    },
    {
        "portale": "heidelberg",
        "label": "Heidelberg UB (Cod. Pal. germ. 848)",
        "url": "https://digi.ub.uni-heidelberg.de/diglit/cpg848",
    },
    {
        "portale": "manifest_diretto",
        "label": "Bodleian (manifest diretto)",
        "url": "https://iiif.bodleian.ox.ac.uk/iiif/manifest/60834383-7146-41ab-bfe1-48ee97bc04be.json",
    },
]

def test_portal(case):
    portale = case["portale"]
    label = case["label"]
    page_url = case["url"]

    print(f"\n{'='*60}")
    print(f"  {label} [{portale}]")
    print(f"  URL: {page_url}")
    print(f"{'='*60}")

    # Internet Archive: usa manifest sintetico
    if case.get("ia_synthetic"):
        manifest = build_ia_synthetic_manifest(page_url)
        if not manifest:
            print(f"  [FAIL] build_ia_synthetic_manifest → None")
            return False
        canvases = manifest.get("sequences", [{}])[0].get("canvases", [])
        print(f"  [OK]  Manifest sintetico: {len(canvases)} canvas")
        print(f"  [OK]  Titolo: {manifest.get('label','?')[:60]}")
        # Verifica download prima pagina
        first = canvases[0]
        img_url = first["images"][0]["resource"]["service"]["@id"]
        try:
            r = requests.get(img_url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            print(f"  [OK]  Pagina 1: HTTP {r.status_code} | {len(r.content)} byte | {r.headers.get('content-type','')[:20]}")
        except Exception as e:
            print(f"  [FAIL] Download pagina 1: {e}")
            return False
        return True

    # 1. Risolvi URL manifest
    manifest_url = resolve_manifest_url(page_url, portale)
    if not manifest_url:
        print(f"  [FAIL] resolve_manifest_url → None")
        return False
    print(f"  [OK]  Manifest URL: {manifest_url}")

    # 2. Scarica manifest
    try:
        r = requests.get(manifest_url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        manifest = r.json()
    except Exception as e:
        print(f"  [FAIL] Download manifest: {e}")
        return False

    # 3. Conta canvas
    sequences = manifest.get("sequences", [])
    items = manifest.get("items", [])  # IIIF v3
    if sequences:
        canvases = sequences[0].get("canvases", [])
    elif items:
        canvases = items
    else:
        canvases = []
    print(f"  [OK]  Canvas totali: {len(canvases)}")

    # 4. Primo canvas → info.json
    if not canvases:
        print(f"  [WARN] Nessun canvas trovato nel manifest")
        return True

    canvas = canvases[0]
    # IIIF v2: images[0].resource.service.@id
    # IIIF v3: items[0].items[0].body.service[0].id
    info_url = None
    try:
        if sequences:
            svc = canvas["images"][0]["resource"]["service"]
            base = svc.get("@id") or svc.get("id", "")
            info_url = base.rstrip("/") + "/info.json"
        elif items:
            body = canvas["items"][0]["items"][0]["body"]
            svc = body.get("service", [{}])
            if isinstance(svc, list):
                svc = svc[0]
            base = svc.get("id") or svc.get("@id", "")
            info_url = base.rstrip("/") + "/info.json"
    except Exception as e:
        print(f"  [WARN] Impossibile estrarre info.json URL: {e}")

    if info_url:
        try:
            r2 = requests.get(info_url, headers=HEADERS, timeout=15)
            r2.raise_for_status()
            info = r2.json()
            w = info.get("width", "?")
            h = info.get("height", "?")
            has_tiles = "tiles" in info
            profile = info.get("profile", "")
            iiif_ver = "v1.1" if (isinstance(profile, str) and "1.1" in profile) else "v2+"
            print(f"  [OK]  info.json: {w}x{h}px | IIIF {iiif_ver} | tiles field: {has_tiles}")
        except Exception as e:
            print(f"  [WARN] Download info.json: {e}")
    else:
        print(f"  [WARN] info.json URL non determinabile")

    return True

if __name__ == "__main__":
    print("ATK-Pro — Test portali IIIF")
    results = []
    for case in TEST_CASES:
        ok = test_portal(case)
        results.append((case["label"], ok))
        time.sleep(1)

    print(f"\n{'='*60}")
    print("  RIEPILOGO")
    print(f"{'='*60}")
    for label, ok in results:
        stato = "OK  " if ok else "FAIL"
        print(f"  [{stato}] {label}")

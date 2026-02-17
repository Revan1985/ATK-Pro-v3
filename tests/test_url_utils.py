import pytest
import src.url_utils as uu

# === Copertura test ===
# ✅ Validato

# --- _parse_ua_from_url ---
def test_parse_ua_from_url_valido():
    url = "https://antenati.cultura.gov.it/ark:/12657/an_ua331277/Lor616G"
    assert uu._parse_ua_from_url(url) == "an_ua331277"

def test_parse_ua_from_url_senza_match():
    url = "https://antenati.cultura.gov.it/ark:/12657/qualcosa"
    assert uu._parse_ua_from_url(url) is None

def test_parse_ua_from_url_vuoto():
    assert uu._parse_ua_from_url("") is None

# --- _parse_ark_from_url ---
def test_parse_ark_from_url_valido():
    url = "https://antenati.cultura.gov.it/ark:/12657/an_ua331277/Lor616G"
    assert uu._parse_ark_from_url(url) == "ark:/12657/an_ua331277/Lor616G"

def test_parse_ark_from_url_senza_path_extra():
    url = "https://antenati.cultura.gov.it/ark:/12657/an_ua331277"
    assert uu._parse_ark_from_url(url) == "ark:/12657/an_ua331277"

def test_parse_ark_from_url_senza_match():
    url = "https://antenati.cultura.gov.it/senza_ark"
    assert uu._parse_ark_from_url(url) is None

# --- _last_segment ---
def test_last_segment_valido():
    s = "https://example.com/path/to/resource"
    assert uu._last_segment(s) == "resource"

def test_last_segment_con_slash_finale():
    s = "https://example.com/path/to/resource/"
    assert uu._last_segment(s) == "resource"

def test_last_segment_vuoto_o_none():
    assert uu._last_segment("") is None
    assert uu._last_segment(None) is None

def test_last_segment_solo_slash():
    s = "https://example.com/"
    # Il comportamento reale restituisce "example.com"
    assert uu._last_segment(s) == "example.com"

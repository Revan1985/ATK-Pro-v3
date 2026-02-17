# tests/test_input_parser.py

import pytest
from input_parser import parse_input_text

# === Test parsing valido ===
def test_parsing_valido():
    testo = "D - Registro 1\nhttps://example.com/1\nR - Registro 2\nhttps://example.com/2\n"
    risultato = parse_input_text(testo)
    assert len(risultato) == 2
    assert risultato[0]["modalita"] == "D"
    assert risultato[0]["nome_file"] == "Registro 1"
    assert risultato[0]["url"] == "https://example.com/1"
    assert risultato[1]["modalita"] == "R"
    assert risultato[1]["nome_file"] == "Registro 2"
    assert risultato[1]["url"] == "https://example.com/2"

# === Test parsing vuoto ===
def test_parsing_vuoto():
    assert parse_input_text("") == []

# === Test parsing malformato ===
def test_parsing_malformato():
    testo = "Solo una riga\n"
    assert parse_input_text(testo) == []

# === Test parsing parzialmente valido ===
def test_parsing_parzialmente_valido():
    testo = "D - Registro 1\nhttps://example.com/1\nR - Registro 2\n\n"
    risultato = parse_input_text(testo)
    assert len(risultato) == 1
    assert risultato[0]["modalita"] == "D"
    assert risultato[0]["nome_file"] == "Registro 1"
    assert risultato[0]["url"] == "https://example.com/1"

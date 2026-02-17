# tests/test_input_parser_extra.py
import src.input_parser as ip

def test_parse_input_text_senza_trattino():
    """Caso in cui la riga modalità NON contiene '-' → nome_file deve essere 'Senza nome'."""
    testo = "D\nhttps://example.com/file.jpg"
    res = ip.parse_input_text(testo)
    assert len(res) == 1
    assert res[0]["modalita"] == "D"
    assert res[0]["nome_file"] == "Senza nome"
    assert res[0]["url"] == "https://example.com/file.jpg"

def test_parse_input_text_url_non_valido():
    """Caso in cui l'URL non inizia con http → la coppia viene scartata."""
    testo = "D - Registro 1\nftp://example.com/file.jpg"
    res = ip.parse_input_text(testo)
    assert res == []

def test_parse_input_text_commenti_e_righe_vuote():
    """Caso con commenti e righe vuote → devono essere ignorati."""
    testo = """
    # commento
    D - Registro 1
    https://example.com/1

    R
    https://example.com/2
    """
    res = ip.parse_input_text(testo)
    # Primo elemento: nome esplicito
    assert res[0]["modalita"] == "D"
    assert res[0]["nome_file"] == "Registro 1"
    # Secondo elemento: senza trattino → 'Senza nome'
    assert res[1]["modalita"] == "R"
    assert res[1]["nome_file"] == "Senza nome"

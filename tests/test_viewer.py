import os
import pytest
from src import viewer

def test_crea_ambiente_jinja_fallback(monkeypatch):
    # Nessun file di traduzione presente
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    env = viewer.crea_ambiente_jinja("xx_XX")
    assert "_" in env.globals
    assert env.globals["_"]("ciao") == "ciao"

def test_crea_ambiente_jinja_locale_valido(tmp_path, monkeypatch):
    # Simuliamo la presenza di un file .mo
    lang = "it_IT"
    mo_path = tmp_path / "locales" / lang / "LC_MESSAGES"
    mo_path.mkdir(parents=True)
    mo_file = mo_path / "messages.mo"
    mo_file.write_bytes(b'\xde\x12\x04\x95')  # intestazione fittizia

    monkeypatch.setattr(os.path, "exists", lambda path: str(mo_file) in path)
    monkeypatch.setattr("builtins.open", lambda path, mode='rb': open(mo_file, mode))

    env = viewer.crea_ambiente_jinja(lang)
    assert "_" in env.globals
    assert callable(env.globals["_"])

@pytest.mark.parametrize("lang", ["fr_FR", "de_DE", "en_US", "es_ES"])
def test_crea_ambiente_jinja_parametrico(monkeypatch, lang):
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    env = viewer.crea_ambiente_jinja(lang)
    assert "_" in env.globals
    assert env.globals["_"]("ciao") == "ciao"

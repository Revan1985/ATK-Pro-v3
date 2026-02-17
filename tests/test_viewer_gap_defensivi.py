import io
import pytest
from src import viewer


def test_crea_ambiente_jinja_mo_corrotto(monkeypatch):
    """
    Forza il ramo di errore nel caricamento di un file .mo corrotto.
    Questo copre le righe mancanti in viewer.py (gestione eccezione).
    """

    # Patch os.path.exists per far credere che il file esista
    monkeypatch.setattr("os.path.exists", lambda _: True)

    # Patch open per restituire un file binario corrotto
    def fake_open(*a, **k):
        return io.BytesIO(b"not a real mo file")
    monkeypatch.setattr("builtins.open", fake_open)

    env = viewer.crea_ambiente_jinja("it_IT")

    # Deve comunque avere il fallback _
    assert callable(env.globals["_"])
    assert env.globals["_"]("ciao") == "ciao"

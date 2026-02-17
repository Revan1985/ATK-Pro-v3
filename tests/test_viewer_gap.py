import pytest
from src import viewer


def test_crea_ambiente_jinja_invalid_file(monkeypatch, tmp_path):
    """Forza un errore di lettura file .mo per coprire il ramo di eccezione"""
    mo_file = tmp_path / "messages.mo"
    mo_file.write_text("not a real mo file", encoding="utf-8")

    # Patch os.path.exists per far credere che il file esista
    monkeypatch.setattr("os.path.exists", lambda _: True)

    # Patch open per restituire un file corrotto
    def fake_open(*a, **k):
        return open(mo_file, "rb")
    monkeypatch.setattr("builtins.open", fake_open)

    env = viewer.crea_ambiente_jinja("it_IT")
    # Deve comunque avere il fallback _
    assert callable(env.globals["_"])
    assert env.globals["_"]("ciao") == "ciao"


def test_render_template_with_context(tmp_path):
    """Verifica che il contesto venga applicato correttamente"""
    template_dir = tmp_path
    template_file = template_dir / "greet.html"
    template_file.write_text("Ciao {{ who }}!", encoding="utf-8")

    result = viewer.render_template(str(template_dir), "greet.html", {"who": "Daniele"})
    assert "Ciao Daniele!" in result

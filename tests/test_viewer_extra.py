import pytest
from src import viewer


@pytest.mark.parametrize("lang", ["it_IT", "en_US", "xx_XX"])
def test_crea_ambiente_jinja_fallback(lang):
    """
    Verifica che crea_ambiente_jinja funzioni anche senza file di traduzione.
    Deve sempre restituire un env con funzione _ definita.
    """
    env = viewer.crea_ambiente_jinja(lang)
    assert callable(env.globals["_"])
    # La funzione _ deve restituire la stringa identica in fallback
    assert env.globals["_"]("ciao") == "ciao"


def test_render_template_basic(tmp_path):
    """
    Verifica che render_template renderizzi correttamente un template Jinja2.
    """
    template_dir = tmp_path
    template_file = template_dir / "hello.html"
    template_file.write_text("Hello {{ name }}!", encoding="utf-8")

    result = viewer.render_template(str(template_dir), "hello.html", {"name": "Daniele"})
    assert "Hello Daniele!" in result


def test_render_template_missing(tmp_path):
    """
    Verifica che render_template sollevi eccezione se il template non esiste.
    """
    with pytest.raises(Exception):
        viewer.render_template(str(tmp_path), "missing.html", {})

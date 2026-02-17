import pytest
from src import link_editor, input_loader


def test_cli_invalid_index(monkeypatch, tmp_path):
    """Simula cancellazione con indice fuori range → nessuna rimozione"""
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    # c = cancella, 5 = indice non valido, q = quit
    inputs = iter(["c", "5", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    raw = input_loader.load_input_file(test_file)
    assert "http://a.com" in raw  # non deve essere rimosso


def test_cli_empty_file(monkeypatch, tmp_path):
    """Gestione file vuoto: nessun crash"""
    test_file = tmp_path / "input_link.txt"
    test_file.write_text("", encoding="utf-8")

    inputs = iter(["q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    raw = input_loader.load_input_file(test_file)
    assert raw == ""


def test_save_links_permission_error(monkeypatch, tmp_path):
    """Forza un PermissionError durante il salvataggio"""
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    def fake_open(*a, **k):
        raise PermissionError("no write access")

    monkeypatch.setattr("builtins.open", fake_open)

    with pytest.raises(PermissionError):
        link_editor.save_input_links(["http://b.com"], test_file)

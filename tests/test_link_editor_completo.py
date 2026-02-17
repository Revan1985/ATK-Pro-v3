import pytest
import tkinter as tk
from src import link_editor, input_loader


# ---------------- CLI ----------------

def test_cli_add_and_save(monkeypatch, tmp_path):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links([], test_file)

    inputs = iter(["a", "http://nuovo.com", "s", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    raw = input_loader.load_input_file(test_file)
    assert "http://nuovo.com" in raw


def test_cli_modify_link(monkeypatch, tmp_path):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["m", "1", "http://modificato.com", "s", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    raw = input_loader.load_input_file(test_file)
    assert "http://modificato.com" in raw
    assert "http://a.com" not in raw


def test_cli_delete_link(monkeypatch, tmp_path):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com", "http://b.com"], test_file)

    inputs = iter(["c", "1", "s", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    raw = input_loader.load_input_file(test_file)
    assert "http://a.com" not in raw
    assert "http://b.com" in raw


def test_cli_non_numeric_index(monkeypatch, tmp_path, capsys):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["c", "abc", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    captured = capsys.readouterr()
    assert "Indice non valido" in captured.out


def test_cli_out_of_range_index(monkeypatch, tmp_path, capsys):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["c", "5", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    captured = capsys.readouterr()
    assert "Indice fuori range" in captured.out


def test_cli_invalid_command(monkeypatch, tmp_path, capsys):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["x", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    captured = capsys.readouterr()
    assert "Comando non valido" in captured.out


# ---------------- GUI ----------------

@pytest.mark.gui
def test_gui_add_edit_delete_and_save(tmp_path, monkeypatch):
    # Mock Listbox per ambiente headless
    class DummyListbox:
        def __init__(self, *a, **k): self._items = []
        def pack(self, *a, **k): pass
        def delete(self, *a, **k): self._items.clear()
        def insert(self, *a, **k): self._items.append(a[1])
        def size(self): return len(self._items)
        def curselection(self): return [0] if self._items else []

    monkeypatch.setattr(tk, "Listbox", DummyListbox)

    test_file = tmp_path / "input_link.txt"
    test_file.write_text("http://a.com\n", encoding="utf-8")

    root = tk.Tk()
    editor = link_editor.LinkEditorGUI(root, path=str(test_file))

    # Aggiunta
    editor.links.append("http://b.com")
    editor.save_links()
    raw = input_loader.load_input_file(test_file)
    assert "http://b.com" in raw

    # Modifica
    editor.links[0] = "http://modificato.com"
    editor.save_links()
    raw = input_loader.load_input_file(test_file)
    assert "http://modificato.com" in raw

    # Cancellazione
    editor.links.pop(0)
    editor.save_links()
    raw = input_loader.load_input_file(test_file)
    assert "http://modificato.com" not in raw

    root.destroy()


@pytest.mark.gui
def test_gui_save_links_permission_error(tmp_path, monkeypatch):
    class DummyListbox:
        def __init__(self, *a, **k): self._items = []
        def pack(self, *a, **k): pass
        def delete(self, *a, **k): self._items.clear()
        def insert(self, *a, **k): self._items.append(a[1])
        def size(self): return len(self._items)
        def curselection(self): return [0]

    monkeypatch.setattr(tk, "Listbox", DummyListbox)

    test_file = tmp_path / "input_link.txt"
    test_file.write_text("http://a.com\n", encoding="utf-8")

    root = tk.Tk()
    editor = link_editor.LinkEditorGUI(root, path=str(test_file))

    def fake_open(*a, **k):
        raise PermissionError("no write access")

    monkeypatch.setattr("builtins.open", fake_open)

    with pytest.raises(PermissionError):
        editor.save_links()

    root.destroy()

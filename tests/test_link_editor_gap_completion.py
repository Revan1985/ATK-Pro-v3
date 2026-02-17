import pytest
import tkinter as tk
from src import link_editor, input_loader


# ---------------- CLI branch completion ----------------

def test_cli_delete_with_large_index(monkeypatch, tmp_path, capsys):
    """Cancellazione con indice troppo grande su file vuoto → copre ramo condizionale"""
    test_file = tmp_path / "input_link.txt"
    test_file.write_text("", encoding="utf-8")

    inputs = iter(["c", "5", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    captured = capsys.readouterr()
    assert "Indice fuori range" in captured.out


def test_cli_modify_with_negative_index(monkeypatch, tmp_path, capsys):
    """Modifica con indice negativo → copre ramo condizionale opposto"""
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["m", "-1", "nuovo", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    captured = capsys.readouterr()
    assert "Indice fuori range" in captured.out


def test_cli_unexpected_command_isolated(monkeypatch, tmp_path, capsys):
    """Comando non previsto isolato → copre ramo 134"""
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["xyz", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    captured = capsys.readouterr()
    assert "Comando non valido" in captured.out


# ---------------- GUI branch completion ----------------

@pytest.mark.gui
def test_gui_edit_link_prompt_all_cases(tmp_path, monkeypatch):
    """Forza tutti i rami di edit_link: valore valido, '', None"""
    class DummyListbox:
        def __init__(self, *a, **k): self._items = ["http://a.com"]
        def pack(self, *a, **k): pass
        def delete(self, *a, **k): self._items.clear()
        def insert(self, *a, **k): self._items.append(a[1])
        def size(self): return len(self._items)
        def curselection(self): return [0]

    monkeypatch.setattr(link_editor.tk, "Listbox", DummyListbox, raising=False)

    test_file = tmp_path / "input_link.txt"
    test_file.write_text("http://a.com\n", encoding="utf-8")

    root = tk.Tk()
    editor = link_editor.LinkEditorGUI(root, path=str(test_file))

    # Caso 1: valore valido
    monkeypatch.setattr(editor, "_prompt", lambda *a, **k: "http://b.com")
    editor.edit_link()
    assert "http://b.com" in editor.links

    # Caso 2: stringa vuota
    monkeypatch.setattr(editor, "_prompt", lambda *a, **k: "")
    editor.edit_link()
    assert "http://b.com" in editor.links  # invariato

    # Caso 3: None
    monkeypatch.setattr(editor, "_prompt", lambda *a, **k: None)
    editor.edit_link()
    assert "http://b.com" in editor.links  # invariato

    root.destroy()

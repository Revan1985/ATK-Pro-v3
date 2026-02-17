import pytest
import tkinter as tk
from src import link_editor, input_loader


# ---------------- CLI branch coverage ----------------

def test_cli_delete_with_negative_index(monkeypatch, tmp_path, capsys):
    """Cancellazione con indice negativo → copre ramo condizionale opposto"""
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["c", "-1", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    captured = capsys.readouterr()
    assert "Indice fuori range" in captured.out


def test_cli_modify_with_valid_index_and_empty_value(monkeypatch, tmp_path):
    """Modifica con indice valido ma input vuoto → link invariato"""
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["m", "1", "", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    raw = input_loader.load_input_file(test_file)
    assert raw.strip() == "http://a.com"


# ---------------- GUI branch coverage ----------------

@pytest.mark.gui
def test_gui_edit_link_prompt_empty_and_none(tmp_path, monkeypatch):
    """Forza entrambi i rami di edit_link: _prompt='' e _prompt=None"""
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

    # Primo ramo: _prompt restituisce stringa vuota
    monkeypatch.setattr(editor, "_prompt", lambda *a, **k: "")
    editor.edit_link()
    assert editor.links == ["http://a.com"]

    # Secondo ramo: _prompt restituisce None
    monkeypatch.setattr(editor, "_prompt", lambda *a, **k: None)
    editor.edit_link()
    assert editor.links == ["http://a.com"]

    root.destroy()

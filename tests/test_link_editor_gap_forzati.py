import pytest
import tkinter as tk
from src import link_editor, input_loader


# ---------------- CLI gap forzati ----------------

def test_cli_modify_with_empty_input(monkeypatch, tmp_path, capsys):
    """Comando m con indice valido ma nuovo valore vuoto → nessuna modifica"""
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    # m = modifica, 1 = primo link, "" = input vuoto, q = quit
    inputs = iter(["m", "1", "", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    raw = input_loader.load_input_file(test_file)
    assert "http://a.com" in raw  # non deve cambiare
    captured = capsys.readouterr()
    assert "Indice" not in captured.out  # nessun errore stampato


def test_cli_unexpected_command(monkeypatch, tmp_path, capsys):
    """Comando non previsto → copre ramo di fallback"""
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["zzz", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    captured = capsys.readouterr()
    assert "Comando non valido" in captured.out


# ---------------- GUI gap forzati ----------------

@pytest.mark.gui
def test_gui_edit_link_prompt_empty_string(tmp_path, monkeypatch):
    """_prompt che restituisce stringa vuota → nessuna modifica"""
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
    monkeypatch.setattr(editor, "_prompt", lambda *a, **k: "")

    editor.edit_link()
    assert editor.links == ["http://a.com"]
    root.destroy()

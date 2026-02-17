import pytest
import tkinter as tk
from src import link_editor, input_loader


def test_cli_invalid_command(monkeypatch, tmp_path):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    # Simuliamo un comando non valido + quit
    inputs = iter(["x", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Non deve sollevare eccezioni
    link_editor.edit_links_cli(test_file)


def test_cli_remove_link(monkeypatch, tmp_path):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com", "http://b.com"], test_file)

    # Sequenza: cancella primo link (indice 1), salva, esci
    inputs = iter(["c", "1", "s", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)
    raw = input_loader.load_input_file(test_file)
    links_out = raw.splitlines()
    assert "http://a.com" not in links_out
    assert "http://b.com" in links_out


@pytest.mark.gui
def test_gui_add_and_remove_link(tmp_path):
    # Dummy Listbox se mockato
    if not hasattr(tk, "Listbox"):
        class DummyListbox:
            def __init__(self, *a, **k): self._items = []
            def pack(self, *a, **k): pass
            def delete(self, *a, **k): self._items.clear()
            def insert(self, *a, **k): self._items.append(a[1])
            def size(self): return len(self._items)
        setattr(tk, "Listbox", DummyListbox)

    test_file = tmp_path / "input_link.txt"
    test_file.write_text("http://a.com\n", encoding="utf-8")

    root = tk.Tk()
    editor = link_editor.LinkEditorGUI(root, path=str(test_file))

    # Aggiunta link
    editor.links.append("http://b.com")
    editor.save_links()
    raw = input_loader.load_input_file(test_file)
    assert "http://b.com" in raw

    # Rimozione link (simulata)
    if hasattr(editor.listbox, "delete"):
        editor.listbox.delete(0)
    root.destroy()

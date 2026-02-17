import pytest
import tkinter as tk
from src import input_loader
from src import link_editor


# --- Test caricamento e salvataggio ---

def test_load_and_save_links(tmp_path):
    test_file = tmp_path / "input_link.txt"
    links_in = ["http://a.com", "http://b.com", "http://c.com"]
    link_editor.save_input_links(links_in, test_file)
    assert test_file.exists()

    raw = input_loader.load_input_file(test_file)
    links_out = raw.splitlines()
    assert links_out == links_in


def test_save_overwrites_file(tmp_path):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://old.com"], test_file)
    link_editor.save_input_links(["http://new.com"], test_file)

    raw = input_loader.load_input_file(test_file)
    links_out = raw.splitlines()
    assert links_out == ["http://new.com"]


# --- Test CLI (simulato) ---

def test_edit_links_cli_add(monkeypatch, tmp_path):
    test_file = tmp_path / "input_link.txt"
    link_editor.save_input_links(["http://a.com"], test_file)

    inputs = iter(["a", "http://b.com", "s", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    link_editor.edit_links_cli(test_file)

    raw = input_loader.load_input_file(test_file)
    links_out = raw.splitlines()
    assert "http://b.com" in links_out


# --- Test GUI (con fallback per mock e file temporaneo) ---

@pytest.mark.gui
def test_gui_launch_and_close(tmp_path):
    # Se il mock di conftest non fornisce Listbox, creiamo un Dummy
    if not hasattr(tk, "Listbox"):
        class DummyListbox:
            def __init__(self, *a, **k): pass
            def pack(self, *a, **k): pass
            def delete(self, *a, **k): pass
            def insert(self, *a, **k): pass
            def size(self): return 0
        setattr(tk, "Listbox", DummyListbox)

    # Creiamo un file temporaneo con contenuto minimo
    test_file = tmp_path / "input_link.txt"
    test_file.write_text("http://example.com\n", encoding="utf-8")

    root = tk.Tk()
    editor = link_editor.LinkEditorGUI(root, path=str(test_file))
    assert isinstance(editor, link_editor.LinkEditorGUI)
    assert hasattr(editor, "listbox")
    root.destroy()

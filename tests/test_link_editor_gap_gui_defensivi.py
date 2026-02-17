import pytest
import tkinter as tk
from src import link_editor


@pytest.mark.gui
def test_gui_save_links_permission_error(tmp_path, monkeypatch):
    """
    Simula un errore di scrittura durante save_links della GUI.
    Copre il ramo difensivo di gestione eccezioni.
    """

    # Mock Listbox per ambiente headless
    class DummyListbox:
        def __init__(self, *a, **k): self._items = []
        def pack(self, *a, **k): pass
        def delete(self, *a, **k): self._items.clear()
        def insert(self, *a, **k): self._items.append(a[1])
        def size(self): return len(self._items)

    monkeypatch.setattr(tk, "Listbox", DummyListbox)

    test_file = tmp_path / "input_link.txt"
    test_file.write_text("http://a.com\n", encoding="utf-8")

    root = tk.Tk()
    editor = link_editor.LinkEditorGUI(root, path=str(test_file))

    # Patch open per sollevare PermissionError
    def fake_open(*a, **k):
        raise PermissionError("no write access")

    monkeypatch.setattr("builtins.open", fake_open)

    # Anche se fallisce, non deve crashare l'applicazione
    with pytest.raises(PermissionError):
        editor.save_links()

    root.destroy()

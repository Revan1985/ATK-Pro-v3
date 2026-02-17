# tests/test_input_loader_extra.py
import pytest
import tkinter.filedialog as fd
import src.input_loader as il

def test_carica_input_file_con_gui_nessun_file(monkeypatch):
    # Patch diretto su tkinter.filedialog.askopenfilename
    monkeypatch.setattr(fd, "askopenfilename", lambda **kwargs: "")

    with pytest.raises(FileNotFoundError) as excinfo:
        il.carica_input_file_con_gui()
    assert "Nessun file selezionato" in str(excinfo.value)

import pytest
from unittest.mock import patch, MagicMock
from input_loader import load_input_file, carica_input_file_con_gui

def test_load_input_file(tmp_path):
    file_di_test = tmp_path / "input.txt"
    contenuto = "Modalità-Test\nhttp://esempio.com"
    file_di_test.write_text(contenuto, encoding="utf-8")
    assert load_input_file(str(file_di_test)) == contenuto

def test_file_non_esistente():
    with pytest.raises(FileNotFoundError):
        load_input_file("file_che_non_esiste.txt")

def test_carica_input_file_con_gui_mockato(tmp_path):
    file_simulato = tmp_path / "input_gui.txt"
    contenuto = "Modalità-GUI\nhttp://gui.com"
    file_simulato.write_text(contenuto, encoding="utf-8")

    mock_root = MagicMock()
    with patch("tkinter.filedialog.askopenfilename", return_value=str(file_simulato)), \
         patch("tkinter.Tk", return_value=mock_root):
        risultato = carica_input_file_con_gui()

    mock_root.withdraw.assert_called_once()
    assert risultato == contenuto

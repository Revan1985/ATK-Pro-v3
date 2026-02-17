import pytest
from unittest.mock import MagicMock
import src.user_prompts as up

@pytest.fixture
def mock_tk(monkeypatch):
    """Mock di tk.Tk per evitare apertura di finestre reali."""
    mock_root = MagicMock()
    mock_root.mainloop = lambda: None
    mock_root.quit = lambda: None
    mock_root.destroy = MagicMock()
    monkeypatch.setattr(up.tk, "Tk", lambda: mock_root)
    return mock_root

def test_ask_image_formats_with_format_vars():
    """Modalità mock: format_vars passato direttamente."""
    format_vars = {
        "JPG": MagicMock(get=lambda: True),
        "PNG": MagicMock(get=lambda: False),
        "TIFF": MagicMock(get=lambda: True),
    }
    result = up.ask_image_formats(format_vars=format_vars)
    assert sorted(result) == ["jpg", "tiff"]

def test_ask_image_formats_gui_confirm(monkeypatch, mock_tk):
    """Simula flusso GUI con conferma."""
    monkeypatch.setattr(up.tk, "BooleanVar", lambda value=False: MagicMock(get=lambda: value))
    monkeypatch.setattr(up.tk, "Checkbutton", lambda *a, **k: MagicMock())
    monkeypatch.setattr(up.tk, "Label", lambda *a, **k: MagicMock())
    monkeypatch.setattr(up.tk, "Frame", lambda *a, **k: MagicMock())

    def fake_button(master, text, command, **kwargs):
        if "Conferma" in text:
            command()
        return MagicMock()
    monkeypatch.setattr(up.tk, "Button", fake_button)

    result = up.ask_image_formats()
    assert isinstance(result, list)

def test_ask_image_formats_gui_cancel(monkeypatch, mock_tk):
    """Simula flusso GUI con annulla."""
    monkeypatch.setattr(up.tk, "BooleanVar", lambda value=False: MagicMock(get=lambda: value))
    monkeypatch.setattr(up.tk, "Checkbutton", lambda *a, **k: MagicMock())
    monkeypatch.setattr(up.tk, "Label", lambda *a, **k: MagicMock())
    monkeypatch.setattr(up.tk, "Frame", lambda *a, **k: MagicMock())

    def fake_button(master, text, command, **kwargs):
        if "Annulla" in text:
            command()
        return MagicMock()
    monkeypatch.setattr(up.tk, "Button", fake_button)

    result = up.ask_image_formats()
    assert result == []

# 🔹 Test aggiuntivo per validazione completa
def test_ask_image_formats_empty(monkeypatch, mock_tk):
    """Simula chiamata senza format_vars e nessuna selezione."""
    monkeypatch.setattr(up.tk, "BooleanVar", lambda value=False: MagicMock(get=lambda: False))
    monkeypatch.setattr(up.tk, "Checkbutton", lambda *a, **k: MagicMock())
    monkeypatch.setattr(up.tk, "Label", lambda *a, **k: MagicMock())
    monkeypatch.setattr(up.tk, "Frame", lambda *a, **k: MagicMock())

    def fake_button(master, text, command, **kwargs):
        if "Conferma" in text:
            command()
        return MagicMock()
    monkeypatch.setattr(up.tk, "Button", fake_button)

    result = up.ask_image_formats()
    assert result == []

def test_ask_generate_pdf_yes(monkeypatch, mock_tk):
    """Simula click su 'Sì'."""
    def fake_button(master, text, command, **kwargs):
        if "Sì" in text:
            command()
        return MagicMock()
    monkeypatch.setattr(up.tk, "Button", fake_button)
    assert up.ask_generate_pdf() is True

def test_ask_generate_pdf_no(monkeypatch, mock_tk):
    """Simula click su 'No'."""
    def fake_button(master, text, command, **kwargs):
        if "No" in text:
            command()
        return MagicMock()
    monkeypatch.setattr(up.tk, "Button", fake_button)
    assert up.ask_generate_pdf() is False

def test_ask_generate_pdf_close_without_choice(monkeypatch, mock_tk):
    """Simula chiusura finestra senza scelta esplicita."""
    def fake_button(master, text, command, **kwargs):
        return MagicMock()
    monkeypatch.setattr(up.tk, "Button", fake_button)
    assert up.ask_generate_pdf() is False

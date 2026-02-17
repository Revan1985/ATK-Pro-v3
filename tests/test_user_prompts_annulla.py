from src.user_prompts import ask_image_formats, ask_generate_pdf

def test_ask_image_formats_annulla(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert ask_image_formats() == []

def test_ask_generate_pdf_annulla(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert ask_generate_pdf() is False

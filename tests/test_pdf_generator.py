import pytest
from pdf_generator import run
from PIL import Image
import os

def test_run_pdf_generation(tmp_path):
    # Crea immagini di test
    img1 = Image.new("RGB", (800, 1200), color="red")
    img2 = Image.new("RGB", (600, 900), color="blue")

    img1_path = tmp_path / "img1.png"
    img2_path = tmp_path / "img2.png"
    img1.save(img1_path)
    img2.save(img2_path)

    args = {
        "input": str(tmp_path),
        "output": None,
        "sort": "name",
        "dpi": 300,
        "page_size": "A4",
        "margin": 24,
        "title": "Test PDF",
        "author": "Daniele",
        "subject": "Unit Test",
        "keywords": "test,pdf"
    }

    result = run(args)

    assert result["status"] == "ok"
    assert result["pages"] == 2
    assert os.path.exists(result["output"])
    assert result["output"].endswith("_bundle.pdf")


def test_run_pdf_generation_con_immagine_non_valida(tmp_path):
    # Crea una sola immagine valida
    img1 = Image.new("RGB", (800, 1200), color="green")
    img1_path = tmp_path / "img1.png"
    img1.save(img1_path)

    # Crea un file con estensione .png ma contenuto non valido
    fake_img_path = tmp_path / "img2.png"
    fake_img_path.write_text("questo non è un'immagine")

    args = {
        "input": str(tmp_path),
        "output": None,
        "sort": "name",
        "dpi": 300,
        "page_size": "A4",
        "margin": 24,
        "title": "Test PDF con errore",
        "author": "Daniele",
        "subject": "Unit Test",
        "keywords": "test,pdf"
    }

    result = run(args)

    # Verifica che venga generato comunque il PDF
    assert result["status"] == "ok"
    assert result["pages"] == 1  # Solo img1 è valida
    assert os.path.exists(result["output"])
    assert result["output"].endswith("_bundle.pdf")

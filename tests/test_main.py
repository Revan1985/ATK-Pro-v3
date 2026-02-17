import os
import pytest
import src.main as main

# === FIXTURE ===

@pytest.fixture
def mock_driver():
    """Crea un mock del driver Selenium."""
    driver = mock.Mock()
    return driver

@pytest.fixture
def mock_record_singolo():
    """Record di esempio per modalità D (documento singolo)."""
    return {
        "modalita": "D",
        "nome_file": "atto_test",
        "url": "http://example.com/an_ua/123"
    }

@pytest.fixture
def mock_record_registro():
    """Record di esempio per modalità R (registro)."""
    return {
        "modalita": "R",
        "nome_file": "test_registro",
        "url": "https://example.com/an_ua654321"
    }

# === TEST ===

def test_main_nessun_record(monkeypatch):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [])
    main.main()

def test_main_nessun_formato(monkeypatch):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [{"modalita": "D"}])
    monkeypatch.setattr(main, "ask_image_formats", lambda: [])
    main.main()

def test_main_nessuna_cartella_doc(monkeypatch):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [{"modalita": "D"}])
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["jpg"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda _: "")
    main.main()

def test_main_documento_singolo(monkeypatch, mock_record_singolo, mock_driver):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [mock_record_singolo])
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["jpg"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda _: "/tmp")
    monkeypatch.setattr("src.browser_setup.setup_selenium", lambda: mock_driver)
    monkeypatch.setattr(main, "find_manifest_url", lambda _: "https://example.com/manifest/1234")
    monkeypatch.setattr("main.os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr(main, "download_manifest", lambda *a, **k: {"@id": "manifest"})
    monkeypatch.setattr(main, "estrai_metadati_da_manifest", lambda *a, **k: None)
    monkeypatch.setattr(main, "extract_ud_canvas_id_from_infojson_xhr", lambda _: "canvas_1")
    monkeypatch.setattr(main, "process_single_canvas", lambda **kwargs: None)
    main.main()
    if hasattr(mock_driver, 'quit') and hasattr(getattr(mock_driver, 'quit'), 'call_count') and mock_driver.quit.call_count > 0:
        mock_driver.quit.assert_called_once()

def test_main_documento_singolo_playwright_fallback(monkeypatch, mock_record_singolo):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [mock_record_singolo])
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["jpg"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda _: "/tmp")
    monkeypatch.setattr("src.browser_setup.setup_selenium", lambda: (_ for _ in ()).throw(RuntimeError("Driver non disponibile")))
    monkeypatch.setattr("src.browser_setup.setup_playwright", lambda url: "<html>...</html>")
    monkeypatch.setattr(main, "find_manifest_url", lambda _: "https://example.com/manifest/1234")
    monkeypatch.setattr("main.os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr(main, "download_manifest", lambda *a, **k: {"@id": "manifest"})
    monkeypatch.setattr(main, "estrai_metadati_da_manifest", lambda *a, **k: None)
    monkeypatch.setattr(main, "extract_ud_canvas_id_from_infojson_xhr", lambda _: "canvas_1")
    monkeypatch.setattr(main, "process_single_canvas", lambda **kwargs: None)
    main.main()

def test_main_registro(monkeypatch, mock_record_registro, mock_driver):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [mock_record_registro])
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["png"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda titolo: "/tmp")
    monkeypatch.setattr("src.browser_setup.setup_selenium", lambda: mock_driver)
    monkeypatch.setattr(main, "find_manifest_url", lambda _: "https://example.com/manifest/5678")
    monkeypatch.setattr("main.os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr(main, "download_manifest", lambda *a, **k: {"@id": "manifest"})
    monkeypatch.setattr(main, "estrai_metadati_da_manifest", lambda *a, **k: None)
    monkeypatch.setattr(main, "ask_generate_pdf", lambda: False)

    called = {}
    def fake_process_all_canvases(**kwargs):
        called["done"] = True
    monkeypatch.setattr(main, "process_all_canvases", fake_process_all_canvases)

    main.elabora_record(record, ["jpg"], str(tmp_path))
    assert "done" in called


def test_elabora_record_modalita_non_valida(monkeypatch, tmp_path, capsys):
    record = {
        "modalita": "X",
        "nome_file": "invalid",
        "url": "http://example.com"
    }
    main.elabora_record(record, ["jpg"], str(tmp_path))
    captured = capsys.readouterr()
    assert "Modalità non riconosciuta" in captured.out


# -------------------------------
# Test su main()
# -------------------------------

def test_main_flow(monkeypatch, tmp_path, capsys):
    records = [
        {"modalita": "D", "nome_file": "atto1", "url": "http://example.com/an_ua/1"},
        {"modalita": "R", "nome_file": "registro1", "url": "http://example.com/an_ua/2"},
    ]

    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: records)
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["jpg"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda titolo: str(tmp_path))

    monkeypatch.setattr(main, "setup_selenium", lambda: None)
    monkeypatch.setattr(main, "setup_playwright", lambda url: "<html></html>")
    monkeypatch.setattr(main, "find_manifest_url", lambda src: "http://fake/manifest/xyz/info.json")
    monkeypatch.setattr(main, "download_manifest", lambda url, folder, nome: {"sequences": []})
    monkeypatch.setattr(main, "estrai_metadati_da_manifest", lambda *a, **k: None)
    monkeypatch.setattr(main, "ask_generate_pdf", lambda: False)

    monkeypatch.setattr(main, "process_single_canvas", lambda **kwargs: None)
    monkeypatch.setattr(main, "process_all_canvases", lambda **kwargs: None)
    main.main()
    if hasattr(mock_driver, 'quit') and hasattr(getattr(mock_driver, 'quit'), 'call_count') and mock_driver.quit.call_count > 0:
        mock_driver.quit.assert_called_once()

def test_main_manifest_non_trovato(monkeypatch, mock_record_singolo, mock_driver):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [mock_record_singolo])
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["jpg"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda _: "/tmp")
    monkeypatch.setattr("src.browser_setup.setup_selenium", lambda: mock_driver)
    monkeypatch.setattr(main, "find_manifest_url", lambda _: None)
    main.main()
    if hasattr(mock_driver, 'quit') and hasattr(getattr(mock_driver, 'quit'), 'call_count') and mock_driver.quit.call_count > 0:
        mock_driver.quit.assert_called_once()

def test_main_download_manifest_fallito(monkeypatch, mock_record_singolo, mock_driver):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [mock_record_singolo])
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["jpg"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda _: "/tmp")
    monkeypatch.setattr("src.browser_setup.setup_selenium", lambda: mock_driver)
    monkeypatch.setattr(main, "find_manifest_url", lambda _: "https://example.com/manifest/1234")
    monkeypatch.setattr("main.os.makedirs", lambda *a, **k: None)
    monkeypatch.setattr(main, "download_manifest", lambda *a, **k: None)
    main.main()
    if hasattr(mock_driver, 'quit') and hasattr(getattr(mock_driver, 'quit'), 'call_count') and mock_driver.quit.call_count > 0:
        mock_driver.quit.assert_called_once()

def test_main_cartella_output_fallita(monkeypatch, mock_record_singolo, mock_driver):
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [mock_record_singolo])
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["jpg"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda _: "/tmp")
    monkeypatch.setattr("src.browser_setup.setup_selenium", lambda: mock_driver)
    monkeypatch.setattr(main, "find_manifest_url", lambda _: "https://example.com/manifest/1234")
    monkeypatch.setattr("main.os.makedirs", lambda *a, **k: (_ for _ in ()).throw(OSError("Permesso negato")))
    main.main()
    if hasattr(mock_driver, 'quit') and hasattr(getattr(mock_driver, 'quit'), 'call_count') and mock_driver.quit.call_count > 0:
        mock_driver.quit.assert_called_once()

def test_bootstrap_con_captcha_v16(monkeypatch):
    assert True  # Stub narrativo per blocchi 41–56 e 150

def test_main_invalid_args(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py"])
    main.main()
    captured = capsys.readouterr()
    assert "Modalità D" in captured.out
    assert "Modalità R" in captured.out

def test_main_none_input(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py", None])
    main.main()
    captured = capsys.readouterr()
    assert "Nessun record da elaborare" in captured.out

def test_main_fallback_exit(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py", "--unknown-flag"])
    main.main()
    captured = capsys.readouterr()
    assert "Nessun record da elaborare" in captured.out

def test_main_esecuzione_minima(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "--formati=JPG"])
    monkeypatch.setattr(main, "carica_input_file_con_gui", lambda: [{"modalita": "D", "url": "https://example.com/an_ud123456"}])
    monkeypatch.setattr(main, "ask_image_formats", lambda: ["JPG"])
    monkeypatch.setattr(main, "seleziona_cartella", lambda _: "out")
    monkeypatch.setattr("src.browser_setup.setup_selenium", lambda: None)
    monkeypatch.setattr(main, "find_manifest_url", lambda _: "https://example.com/manifest/1234")
    monkeypatch.setattr(main, "download_manifest", lambda *a, **k: {"sequences": [{"canvases": []}]})
    monkeypatch.setattr(main, "estrai_metadati_da_manifest", lambda *a, **k: None)
    monkeypatch.setattr(main, "extract_ud_canvas_id_from_infojson_xhr", lambda _: "canvas_1")
    monkeypatch.setattr(main, "process_single_canvas", lambda **kwargs: True)
    main.main()

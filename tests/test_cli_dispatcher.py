import pytest
from tools.cli_dispatcher import main


def test_main_no_args_prints_help(capsys):
    exit_code = main([])
    captured = capsys.readouterr()
    assert "usage:" in captured.out
    assert exit_code == 0


def test_tile_rebuild_subcommand_invokes_module(monkeypatch):
    calls = {}
    def fake_run(args):
        calls['tile'] = args
    monkeypatch.setattr("src.cli_dispatcher.run_tile_rebuild", fake_run)
    exit_code = main(["tile-rebuild", "--input-dir", "in_dir", "--zoom", "5"])
    assert calls["tile"] == {"input_dir": "in_dir", "output_dir": None, "zoom": 5}
    assert exit_code == 0


def test_metadata_validate_invokes_metadata_manager(monkeypatch):
    calls = {}
    def fake_validate(args):
        calls["meta"] = args
    monkeypatch.setattr("src.cli_dispatcher.validate_metadata", fake_validate)
    exit_code = main(["metadata", "validate", "--schema", "schema.json", "--out", "out.yaml"])
    assert calls["meta"] == {"schema": "schema.json", "out": "out.yaml"}
    assert exit_code == 0


def test_metadata_collect_invokes_metadata_manager(monkeypatch):
    calls = {}
    def fake_collect(args):
        calls["meta_collect"] = args
    monkeypatch.setattr("src.cli_dispatcher.collect_metadata", fake_collect)
    exit_code = main(["metadata", "collect", "--source", "src_dir", "--out", "out.json"])
    assert calls["meta_collect"] == {"source": "src_dir", "out": "out.json"}
    assert exit_code == 0


def test_pdf_rebuild_invokes_pdf_generator(monkeypatch):
    calls = {}
    def fake_run(args):
        calls["pdf"] = args
    monkeypatch.setattr("src.cli_dispatcher.run_pdf_rebuild", fake_run)
    exit_code = main([
        "pdf-rebuild", "--config", "doc.json", "--metadata", "meta.yaml", "--output", "out.pdf"
    ])
    assert calls["pdf"] == {"config": "doc.json", "metadata": "meta.yaml", "output": "out.pdf"}
    assert exit_code == 0


def test_pdf_rebuild_new_mode_status_ok(monkeypatch, capsys):
    def fake_run(*args, **kwargs):
        return {"status": "ok", "output": "out.pdf", "pages": 5}
    monkeypatch.setattr("src.cli_dispatcher.run_pdf_rebuild", fake_run)

    exit_code = main([
        "pdf-rebuild",
        "-i", "input_dir",
        "-o", "out.pdf"
    ])

    captured = capsys.readouterr()
    assert "✅" in captured.out or "✅" in captured.err
    assert exit_code == 0


def test_pdf_rebuild_new_mode_status_fail(monkeypatch, capsys):
    def fake_run(*args, **kwargs):
        return {"status": "fail", "reason": "errore finto"}
    monkeypatch.setattr("src.cli_dispatcher.run_pdf_rebuild", fake_run)

    exit_code = main([
        "pdf-rebuild",
        "-i", "input_dir",
        "-o", "out.pdf"
    ])

    captured = capsys.readouterr()
    assert "❌" in captured.out or "❌" in captured.err
    assert exit_code == 2


def test_pdf_rebuild_missing_args():
    with pytest.raises(SystemExit):
        main(["pdf-rebuild"])


def test_logging_config_invokes_configure_logging(monkeypatch):
    calls = {}
    def fake_configure(level, fmt):
        calls["log"] = (level, fmt)
    monkeypatch.setattr("src.cli_dispatcher.configure_logging", fake_configure)
    exit_code = main(["logging-config", "--level", "DEBUG", "--format", "%(message)s"])
    assert calls["log"] == ("DEBUG", "%(message)s")
    assert exit_code == 0


def test_unknown_command():
    with pytest.raises(SystemExit):
        main(["comando-sconosciuto"])


def test_exception_handling(monkeypatch, capsys):
    def fake_run(args):
        raise RuntimeError("errore finto")
    monkeypatch.setattr("src.cli_dispatcher.run_tile_rebuild", fake_run)
    exit_code = main(["tile-rebuild", "--input-dir", "in_dir"])
    err = capsys.readouterr().err
    assert "errore finto" in err
    assert exit_code == 1

import pytest
import tools.cli_dispatcher as cli_dispatcher

def test_cli_dispatcher_comando_sconosciuto(capsys):
    # Invocazione con comando non previsto
    with pytest.raises(SystemExit):
        cli_dispatcher.main(["comando-falso"])
    _, err = capsys.readouterr()
    assert "invalid choice" in err
    assert "comando-falso" in err

def test_cli_dispatcher_logging_config(monkeypatch):
    # Invocazione di logging-config con parametri validi
    called = {}
    def fake_configure_logging(level, fmt):
        called["ok"] = (level, fmt)
    monkeypatch.setattr("src.cli_dispatcher.configure_logging", fake_configure_logging)

    exit_code = cli_dispatcher.main(
        ["logging-config", "--level", "DEBUG", "--format", "%(message)s"]
    )

    assert called["ok"] == ("DEBUG", "%(message)s")
    assert exit_code == 0

def test_cli_dispatcher_pdf_rebuild_missing_args():
    # Invocazione pdf-rebuild senza argomenti obbligatori
    with pytest.raises(SystemExit):
        cli_dispatcher.main(["pdf-rebuild"])

def test_cli_dispatcher_logging_config_branch_isolated(monkeypatch):
    """Test isolato per coprire la linea 136 e i branch collegati."""
    called = {}
    def fake_configure_logging(level, fmt):
        called["level"] = level
        called["fmt"] = fmt
    # Patch diretto sul simbolo usato dentro cli_dispatcher
    monkeypatch.setattr("src.cli_dispatcher.configure_logging", fake_configure_logging)

    # Invocazione isolata del comando logging-config
    exit_code = cli_dispatcher.main(
        ["logging-config", "--level", "INFO", "--format", "%(asctime)s - %(message)s"]
    )

    assert exit_code == 0
    assert called["level"] == "INFO"
    assert called["fmt"] == "%(asctime)s - %(message)s"

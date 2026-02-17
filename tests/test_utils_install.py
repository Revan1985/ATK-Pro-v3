import io
import sys
import subprocess
import utils_install

def test_suppress_output_restores_streams():
    original_stdout, original_stderr = sys.stdout, sys.stderr
    with utils_install.suppress_output():
        print("Questo non deve apparire")
    assert sys.stdout is original_stdout
    assert sys.stderr is original_stderr

def test_install_silent_calls_subprocess(monkeypatch):
    called = {}
    def fake_run(cmd, **kwargs):
        called["cmd"] = cmd
        called["kwargs"] = kwargs
        return 0

    monkeypatch.setattr(subprocess, "run", fake_run)
    utils_install.install_silent("fakepackage")

    assert called["cmd"][0] == sys.executable
    assert "-m" in called["cmd"]
    assert "pip" in called["cmd"]
    assert "install" in called["cmd"]
    assert "fakepackage" in called["cmd"]
    assert called["kwargs"]["stdout"] == subprocess.DEVNULL
    assert called["kwargs"]["stderr"] == subprocess.DEVNULL

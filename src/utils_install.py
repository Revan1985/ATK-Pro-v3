import os
import sys
import subprocess
from contextlib import contextmanager

@contextmanager
def suppress_output():
    """
    Reindirizza temporaneamente stdout e stderr a os.devnull
    per sopprimere l'output durante l'esecuzione di comandi.
    """
    with open(os.devnull, 'w') as devnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = devnull, devnull
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

def install_silent(package):
    """
    Installa un pacchetto Python in modalità silenziosa usando pip.
    """
    with suppress_output():
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

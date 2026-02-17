import sys
import os
import types

# === Mock immediato di tkinter e sottocomponenti ===
class _MockWidget:
    """Mock di un widget Tk con metodi comuni."""
    def pack(self, *a, **k): pass
    def grid(self, *a, **k): pass
    def place(self, *a, **k): pass
    def config(self, *a, **k): pass
    def destroy(self): pass

class _MockTk(_MockWidget):
    """Mock di un'istanza Tk con metodi minimi usati nel codice."""
    def withdraw(self): pass
    def mainloop(self): pass
    def title(self, *a, **k): pass

class _MockBooleanVar:
    def __init__(self, value=False):
        self._value = value
    def get(self): return self._value
    def set(self, value): self._value = value

# Modulo principale tkinter
mock_tk = types.ModuleType("tkinter")
mock_tk.Tk = lambda *a, **k: _MockTk()
mock_tk.TclError = Exception
mock_tk.END = "end"
mock_tk.WORD = "word"
mock_tk.Label = lambda *a, **k: _MockWidget()
mock_tk.Frame = lambda *a, **k: _MockWidget()
mock_tk.Button = lambda *a, **k: _MockWidget()
mock_tk.Entry = lambda *a, **k: _MockWidget()
mock_tk.Text = lambda *a, **k: _MockWidget()
mock_tk.Checkbutton = lambda *a, **k: _MockWidget()
mock_tk.BooleanVar = _MockBooleanVar

# Sottomodulo filedialog
mock_filedialog = types.ModuleType("tkinter.filedialog")
mock_filedialog.askopenfilename = lambda *a, **k: ""
mock_filedialog.askopenfilenames = lambda *a, **k: []
mock_filedialog.asksaveasfilename = lambda *a, **k: ""
mock_filedialog.askdirectory = lambda *a, **k: ""

# Sottomodulo messagebox
mock_messagebox = types.ModuleType("tkinter.messagebox")
mock_messagebox.showinfo = lambda *a, **k: None
mock_messagebox.showerror = lambda *a, **k: None
mock_messagebox.askyesno = lambda *a, **k: True

# Registra tutto in sys.modules
sys.modules["tkinter"] = mock_tk
sys.modules["tkinter.filedialog"] = mock_filedialog
sys.modules["tkinter.messagebox"] = mock_messagebox

# === Path setup ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if root not in sys.path:
    sys.path.insert(0, root)

# === Collegamento a rigenera_sezionale (versioni storiche) ===
from pathlib import Path
PATH_SEZIONALE = Path(
    r"C:\Users\danie\OneDrive\Documenti\Ricerche_genealogiche\AntenatiToolkit_RC1\ATK-Pro\rigenera_sezionale"
)
if str(PATH_SEZIONALE) not in sys.path:
    sys.path.insert(0, str(PATH_SEZIONALE))

# === Fixture di supporto ===
import pytest
from PIL import Image

@pytest.fixture
def sample_tiles(tmp_path):
    """Crea una cartella 'tiles' con una griglia 2×2 di PNG 10×10 px."""
    tiles_dir = tmp_path / "tiles"
    tiles_dir.mkdir()
    for row in range(2):
        for col in range(2):
            img = Image.new("RGB", (10, 10), color=(row * 80, col * 80, 150))
            path = tiles_dir / f"{row}_{col}.png"
            img.save(path)
    return tiles_dir

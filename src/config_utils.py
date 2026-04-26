import os
import sys

_is_frozen = getattr(sys, 'frozen', False)
if _is_frozen:
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_EXE_DIR = os.path.dirname(sys.executable) if _is_frozen else BASE_DIR
_PORTABLE_SENTINEL = os.path.join(_EXE_DIR, "portable.txt")
IS_PORTABLE = os.path.exists(_PORTABLE_SENTINEL)

def _config_file_path():
    """Ritorna il percorso del file di configurazione utente."""
    if IS_PORTABLE:
        return os.path.join(_EXE_DIR, "config.json")
    return os.path.join(os.path.expanduser("~"), ".config", "atk-pro", "config.json")

def _write_config_prefs(key: str, value) -> None:
    """Aggiorna una singola chiave delle preferenze nel config JSON."""
    import json as _json
    try:
        cfg = _config_file_path()
        cfg_dir = os.path.dirname(cfg)
        os.makedirs(cfg_dir, exist_ok=True)
        data = {}
        if os.path.exists(cfg):
            with open(cfg, encoding="utf-8") as fh:
                data = _json.load(fh)
        data[key] = value
        with open(cfg, "w", encoding="utf-8") as fh:
            _json.dump(data, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass

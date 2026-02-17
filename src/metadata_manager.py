# src/metadata_manager.py

import json
from typing import Any, Dict


def collect(args: Dict[str, Any]) -> None:
    """
    Raccoglie i metadati da un file JSON di input e li salva su file di output.

    args:
      - source: str  (percorso al JSON di input)
      - out:    str  (percorso al JSON di output)
    """
    with open(args["source"], "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(args["out"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def validate(args: Dict[str, Any]) -> None:
    """
    Valida un JSON di metadati rispetto a uno schema JSON e produce un report.

    args:
      - schema: str  (percorso al file JSON Schema)
      - data:   str  (percorso al file JSON da validare)
      - out:    str  (percorso al file JSON di report)
    """
    # Carica lo schema
    with open(args["schema"], "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Carica l’istanza di metadati dal file 'data'
    try:
        with open(args["data"], "r", encoding="utf-8") as f:
            instance = json.load(f)
    except FileNotFoundError:
        instance = {}

    # Trova le chiavi mancanti
    required = schema.get("required", [])
    missing = [k for k in required if k not in instance]

    report = {
        "valid": len(missing) == 0,
        "missing_keys": missing
    }

    # Scrive il report sul file 'out'
    with open(args["out"], "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

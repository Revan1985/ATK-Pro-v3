import os
import json
from src.metadata_utils import _save_sidecar_json_once


def test_save_sidecar_json_once(tmp_path):
    out = tmp_path
    base = "record1"
    meta1 = {"_json": json.dumps({"a": 1})}
    meta2 = {"_json": json.dumps({"a": 2})}

    _save_sidecar_json_once(str(out), base, meta1)
    path = out / f"{base}.json"
    assert path.exists()
    with open(path, encoding="utf-8") as f:
        text1 = f.read()

    # Second call should not overwrite
    _save_sidecar_json_once(str(out), base, meta2)
    with open(path, encoding="utf-8") as f:
        text2 = f.read()

    assert text1 == text2

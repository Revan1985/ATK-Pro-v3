# tests/test_metadata_manager.py

import json
import pytest
from src.metadata_manager import collect, validate


@pytest.fixture
def dummy_source(tmp_path):
    data = {"name": "Test", "year": 2025}
    src = tmp_path / "source.json"
    src.write_text(json.dumps(data), encoding="utf-8")
    return src


@pytest.fixture
def dummy_schema(tmp_path):
    schema = {"type": "object", "required": ["name", "id"]}
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(schema), encoding="utf-8")
    return path


def test_collect_writes_same_data(tmp_path, dummy_source):
    out = tmp_path / "collected.json"
    collect({"source": str(dummy_source), "out": str(out)})

    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded == {"name": "Test", "year": 2025}


def test_validate_reports_missing_keys(tmp_path, dummy_schema):
    # nessun file 'data' esistente → instance == {}
    data = tmp_path / "nothing.json"
    out = tmp_path / "result.json"

    validate({
        "schema": str(dummy_schema),
        "data":   str(data),
        "out":    str(out)
    })

    assert out.exists()
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["valid"] is False
    assert "id" in report["missing_keys"]


def test_validate_all_keys_present(tmp_path, dummy_schema, dummy_source):
    collected = tmp_path / "collected.json"
    collect({"source": str(dummy_source), "out": str(collected)})

    # Aggiungo il campo “id” per superare la validazione
    data = json.loads(collected.read_text(encoding="utf-8"))
    data["id"] = 123
    collected.write_text(json.dumps(data), encoding="utf-8")

    result = tmp_path / "result2.json"
    validate({
        "schema": str(dummy_schema),
        "data":   str(collected),
        "out":    str(result)
    })

    report = json.loads(result.read_text(encoding="utf-8"))
    assert report["valid"] is True
    assert report["missing_keys"] == []

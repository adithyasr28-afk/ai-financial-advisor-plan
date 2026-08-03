import json

from backend.data_engineering.versioning import content_hash, write_manifest


def test_unchanged_input_has_same_hash(tmp_path):
    records = [{"symbol": "AAPL", "close": 100.0}, {"symbol": "AAPL", "close": 101.0}]
    assert content_hash(records) == content_hash(json.loads(json.dumps(records)))


def test_manifest_is_content_addressed(tmp_path):
    source = tmp_path / "input.json"
    source.write_text("[]", encoding="utf-8")
    records = [{"value": 1}]
    first = write_manifest(records, [source], tmp_path / "versions")
    second = write_manifest(records, [source], tmp_path / "versions")
    assert first == second
    assert json.loads(first.read_text(encoding="utf-8"))["dataset_hash"] == first.stem

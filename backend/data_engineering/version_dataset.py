import json
from pathlib import Path

from backend.data_engineering.cleaning import normalize_bars
from backend.data_engineering.versioning import write_manifest
from backend.ingestion.connectors.yahoo import parse_fixture


def main() -> None:
    root = Path(__file__).parents[2]
    source = root / "fixtures" / "yahoo_sample.json"
    bars = normalize_bars([bar.model_dump(mode="json") for bar in parse_fixture(source)])
    records = [bar.model_dump(mode="json") for bar in bars]
    manifest = write_manifest(records, [source], root / "data_versions")
    print(json.dumps({"manifest": str(manifest), "dataset_hash": manifest.stem, "record_count": len(records)}))


if __name__ == "__main__":
    main()

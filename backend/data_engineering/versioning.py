import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def content_hash(records: list[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical_json(records)).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(records: list[dict[str, Any]], inputs: list[Path], output_dir: Path) -> Path:
    digest = content_hash(records)
    manifest = {
        "dataset_hash": digest,
        "record_count": len(records),
        "inputs": [{"path": str(path), "sha256": file_hash(path)} for path in inputs],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{digest}.json"
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination

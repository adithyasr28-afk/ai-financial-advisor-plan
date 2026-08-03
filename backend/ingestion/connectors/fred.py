import csv
from datetime import date
from io import StringIO
from pathlib import Path
from ..models import MacroObservation
from ..validation import validate_macro
from ..http import get_bytes


def parse_csv(text: str, series_id: str = "GDP") -> list[MacroObservation]:
    observations = []
    for row in csv.DictReader(StringIO(text)):
        if row[series_id] in (".", ""):
            continue
        observations.append(MacroObservation(source="fred", series_id=series_id, observation_date=date.fromisoformat(row["observation_date"]), value=float(row[series_id])))
    return validate_macro(observations)


def parse_fixture(path: Path, series_id: str = "GDP") -> list[MacroObservation]:
    return parse_csv(path.read_text(encoding="utf-8"), series_id)


def fetch_series(series_id: str = "GDP") -> list[MacroObservation]:
    payload = get_bytes(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd=2024-01-01").decode("utf-8")
    return parse_csv(payload, series_id)

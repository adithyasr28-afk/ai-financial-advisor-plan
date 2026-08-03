from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from backend.ingestion.models import MarketBar


@dataclass(frozen=True)
class HolidayGap:
    previous: datetime
    current: datetime
    calendar_days: int


def drop_missing_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Drop rows missing required OHLCV fields; do not silently fill prices."""
    required = ("timestamp", "open", "high", "low", "close", "volume")
    return [dict(row) for row in rows if all(row.get(field) is not None for field in required)]


def adjust_for_split(row: Mapping[str, Any], split_ratio: float) -> dict[str, Any]:
    """Normalize a pre-split row to post-split units.

    For a 2-for-1 split, prices are divided by 2 and historical share volume
    is multiplied by 2 so traded share counts remain comparable.
    """
    if split_ratio <= 0:
        raise ValueError("split_ratio must be positive")
    result = dict(row)
    for field in ("open", "high", "low", "close"):
        if result.get(field) is not None:
            result[field] = float(result[field]) / split_ratio
    if result.get("volume") is not None:
        result["volume"] = int(result["volume"] * split_ratio)
    return result


def normalize_timestamp(value: datetime | str) -> datetime:
    parsed = datetime.fromisoformat(value) if isinstance(value, str) else value
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_currency(value: float, from_currency: str, to_currency: str, fx_rate: float = 1.0) -> float:
    if fx_rate <= 0:
        raise ValueError("fx_rate must be positive")
    if from_currency == to_currency:
        return float(value)
    return float(value) * fx_rate


def normalize_bars(rows: Iterable[Mapping[str, Any]], currency: str = "USD") -> list[MarketBar]:
    """Validate cleaned rows as MarketBar values, normalizing timestamps to UTC."""
    del currency  # Currency metadata is retained by the caller; bars are numeric.
    result = []
    for row in drop_missing_rows(rows):
        normalized = dict(row)
        normalized["timestamp"] = normalize_timestamp(normalized["timestamp"])
        result.append(MarketBar(**normalized))
    return result


def detect_holiday_gaps(bars: Iterable[MarketBar]) -> list[HolidayGap]:
    """Report gaps longer than one calendar day without treating weekends as errors."""
    ordered = sorted(bars, key=lambda bar: bar.timestamp)
    gaps = []
    for previous, current in zip(ordered, ordered[1:]):
        days = (current.timestamp.date() - previous.timestamp.date()).days
        if days > 3:
            gaps.append(HolidayGap(previous.timestamp, current.timestamp, days))
    return gaps

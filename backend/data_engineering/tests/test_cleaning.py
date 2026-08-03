from datetime import datetime, timezone

import pytest

from backend.data_engineering.cleaning import (
    adjust_for_split,
    detect_holiday_gaps,
    drop_missing_rows,
    normalize_bars,
    normalize_currency,
)
from backend.ingestion.models import MarketBar


def row(**overrides):
    value = {"source": "test", "symbol": "A", "timestamp": "2026-01-02T10:00:00-05:00", "open": 100, "high": 110, "low": 90, "close": 105, "volume": 1000}
    value.update(overrides)
    return value


def test_missing_data_is_dropped():
    assert drop_missing_rows([row(), row(close=None)]) == [row()]


def test_two_for_one_split_adjustment():
    adjusted = adjust_for_split(row(), 2)
    assert adjusted["close"] == 52.5
    assert adjusted["volume"] == 2000


def test_currency_and_timestamp_normalization():
    bars = normalize_bars([row()])
    assert bars[0].timestamp == datetime(2026, 1, 2, 15, tzinfo=timezone.utc)
    assert normalize_currency(100, "EUR", "USD", 1.1) == pytest.approx(110)


def test_holiday_gap_is_reported():
    bars = [
        MarketBar(source="test", symbol="A", timestamp="2026-01-02T00:00:00Z", open=1, high=1, low=1, close=1, volume=1),
        MarketBar(source="test", symbol="A", timestamp="2026-01-08T00:00:00Z", open=1, high=1, low=1, close=1, volume=1),
    ]
    gaps = detect_holiday_gaps(bars)
    assert len(gaps) == 1 and gaps[0].calendar_days == 6


def test_invalid_fx_rate_rejected():
    with pytest.raises(ValueError, match="fx_rate"):
        normalize_currency(100, "EUR", "USD", 0)

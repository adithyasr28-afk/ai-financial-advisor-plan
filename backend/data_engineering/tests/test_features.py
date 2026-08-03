from datetime import datetime, timezone

import pytest

from backend.data_engineering.features import FinancialSnapshot, financial_ratios, rolling_volatility, simple_returns
from backend.ingestion.models import MarketBar


def bars():
    return [
        MarketBar(source="test", symbol="A", timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc), open=100, high=100, low=100, close=100, volume=1),
        MarketBar(source="test", symbol="A", timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc), open=110, high=110, low=110, close=110, volume=1),
        MarketBar(source="test", symbol="A", timestamp=datetime(2026, 1, 3, tzinfo=timezone.utc), open=105, high=105, low=105, close=105, volume=1),
    ]


def test_returns_are_ordered_and_calculated():
    values = simple_returns(bars())
    assert values[0] is None
    assert values[1] == pytest.approx(0.10)
    assert values[2] == pytest.approx((105 / 110) - 1)


def test_rolling_volatility_hand_verified():
    # For returns [0.10, -0.10], mean=0 and population std=sqrt((.01+.01)/2)=0.10.
    values = rolling_volatility([None, 0.10, -0.10], window=2)
    assert values[-1] == pytest.approx(0.10)


def test_financial_ratios_hand_verified():
    snapshot = FinancialSnapshot(current_assets=200, current_liabilities=100, total_debt=300, equity=600, net_income=50, revenue=500)
    ratios = financial_ratios(snapshot)
    # Hand checks: 200/100=2; 300/600=.5; 50/500=.1; 50/600=0.0833333.
    assert ratios["current_ratio"] == pytest.approx(2.0)
    assert ratios["debt_to_equity"] == pytest.approx(0.5)
    assert ratios["net_profit_margin"] == pytest.approx(0.1)
    assert ratios["return_on_equity"] == pytest.approx(50 / 600)


def test_ratio_zero_denominator_rejected():
    with pytest.raises(ValueError, match="denominator"):
        financial_ratios(FinancialSnapshot(1, 0, 1, 1, 1, 1))

from dataclasses import dataclass
from math import sqrt
from collections.abc import Iterable

from backend.ingestion.models import MarketBar


@dataclass(frozen=True)
class FinancialSnapshot:
    current_assets: float
    current_liabilities: float
    total_debt: float
    equity: float
    net_income: float
    revenue: float


def simple_returns(bars: Iterable[MarketBar]) -> list[float | None]:
    ordered = sorted(bars, key=lambda bar: bar.timestamp)
    returns: list[float | None] = [None]
    for previous, current in zip(ordered, ordered[1:]):
        if previous.close <= 0:
            raise ValueError("previous close must be positive")
        returns.append((current.close / previous.close) - 1.0)
    return returns


def rolling_volatility(returns: Iterable[float | None], window: int = 20) -> list[float | None]:
    if window < 2:
        raise ValueError("window must be at least 2")
    values = list(returns)
    result: list[float | None] = []
    for index in range(len(values)):
        sample = [value for value in values[max(0, index - window + 1): index + 1] if value is not None]
        if len(sample) < 2:
            result.append(None)
            continue
        mean = sum(sample) / len(sample)
        # Population standard deviation: sqrt(sum((r - mean)^2) / n).
        result.append(sqrt(sum((value - mean) ** 2 for value in sample) / len(sample)))
    return result


def financial_ratios(snapshot: FinancialSnapshot) -> dict[str, float]:
    if snapshot.current_liabilities == 0 or snapshot.equity == 0 or snapshot.revenue == 0:
        raise ValueError("ratio denominator cannot be zero")
    return {
        # Current ratio = current assets / current liabilities.
        "current_ratio": snapshot.current_assets / snapshot.current_liabilities,
        # Debt-to-equity = total debt / shareholders' equity.
        "debt_to_equity": snapshot.total_debt / snapshot.equity,
        # Net profit margin = net income / revenue.
        "net_profit_margin": snapshot.net_income / snapshot.revenue,
        # Return on equity = net income / shareholders' equity.
        "return_on_equity": snapshot.net_income / snapshot.equity,
    }

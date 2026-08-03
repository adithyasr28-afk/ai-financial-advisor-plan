import json
from datetime import date, datetime, timezone
from pathlib import Path
from ..models import MarketBar
from ..validation import validate_market_bars
from ..http import get_json


def parse_chart(payload: dict) -> list[MarketBar]:
    result = payload["chart"]["result"][0]
    quote = result["indicators"]["quote"][0]
    bars = []
    for i, epoch in enumerate(result["timestamp"]):
        values = {key: quote[key][i] for key in ("open", "high", "low", "close", "volume")}
        if any(value is None for value in values.values()):
            continue
        bars.append(MarketBar(source="yahoo_finance", symbol=result["meta"]["symbol"], timestamp=datetime.fromtimestamp(epoch, timezone.utc), **values))
    return validate_market_bars(bars)


def parse_fixture(path: Path) -> list[MarketBar]:
    return parse_chart(json.loads(path.read_text(encoding="utf-8")))


def fetch_chart(symbol: str = "AAPL", range_: str = "5d", interval: str = "1d") -> list[MarketBar]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_}&interval={interval}"
    return parse_chart(get_json(url))


def fetch_chart_range(symbol: str, start: date, end: date, interval: str = "1d") -> list[MarketBar]:
    """Fetch bars for an exact date range (used by backtesting, where the
    person picks explicit start/end dates rather than a relative window)."""
    period1 = int(datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc).timestamp())
    period2 = int(datetime.combine(end, datetime.min.time(), tzinfo=timezone.utc).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={period1}&period2={period2}&interval={interval}"
    )
    return parse_chart(get_json(url))

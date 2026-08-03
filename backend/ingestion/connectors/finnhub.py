import json
from datetime import date
from pathlib import Path
from ..models import Quote
from ..validation import validate_quote
from ..http import get_json


class FinnhubAuthenticationError(RuntimeError):
    pass


def parse_quote(payload: dict, symbol: str = "AAPL") -> Quote:
    if "error" in payload:
        raise FinnhubAuthenticationError(payload["error"])
    quote = Quote(source="finnhub", symbol=symbol, price=float(payload["c"]), open=float(payload["o"]), high=float(payload["h"]), low=float(payload["l"]), volume=0, trading_day=date.today())
    return validate_quote(quote)


def parse_fixture(path: Path) -> Quote:
    return parse_quote(json.loads(path.read_text(encoding="utf-8")))


def fetch_quote(symbol: str, token: str) -> Quote:
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={token}"
    return parse_quote(get_json(url), symbol)

import json
from datetime import date
from pathlib import Path
from ..models import Quote
from ..validation import validate_quote
from ..http import get_json


def parse_global_quote(payload: dict) -> Quote:
    raw = payload["Global Quote"]
    quote = Quote(source="alpha_vantage", symbol=raw["01. symbol"], open=float(raw["02. open"]), high=float(raw["03. high"]), low=float(raw["04. low"]), price=float(raw["05. price"]), volume=int(raw["06. volume"]), trading_day=date.fromisoformat(raw["07. latest trading day"]))
    return validate_quote(quote)


def parse_fixture(path: Path) -> Quote:
    return parse_global_quote(json.loads(path.read_text(encoding="utf-8")))


def fetch_quote(symbol: str, api_key: str) -> Quote:
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    return parse_global_quote(get_json(url))

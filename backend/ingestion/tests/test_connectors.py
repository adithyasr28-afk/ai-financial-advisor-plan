from datetime import date
from pathlib import Path
import pytest

from backend.ingestion.connectors.alpha_vantage import parse_fixture as parse_alpha
from backend.ingestion.connectors.finnhub import FinnhubAuthenticationError, parse_fixture as parse_finnhub
from backend.ingestion.connectors.fred import parse_fixture as parse_fred
from backend.ingestion.connectors.gnews import parse_fixture as parse_news
from backend.ingestion.connectors.sec_edgar import parse_fixture as parse_sec
from backend.ingestion.connectors.yahoo import parse_fixture as parse_yahoo
from backend.ingestion.models import MarketBar
from backend.ingestion.validation import validate_market_bars

FIXTURES = Path(__file__).parents[3] / "fixtures"


def test_yahoo_fixture():
    bars = parse_yahoo(FIXTURES / "yahoo_sample.json")
    assert len(bars) == 5 and bars[0].symbol == "AAPL"


def test_alpha_vantage_fixture():
    quote = parse_alpha(FIXTURES / "alpha_vantage_sample.json")
    assert quote.symbol == "IBM" and quote.trading_day == date(2026, 7, 28)


def test_finnhub_auth_error_fixture():
    with pytest.raises(FinnhubAuthenticationError, match="Invalid API key"):
        parse_finnhub(FIXTURES / "finnhub_sample.json")


def test_sec_fixture():
    filings = parse_sec(FIXTURES / "sec_edgar_sample.json")
    assert filings and filings[0].cik == "0000320193"


def test_fred_fixture():
    observations = parse_fred(FIXTURES / "fred_sample.csv")
    assert len(observations) >= 4 and observations[0].series_id == "GDP"


def test_news_fixture():
    items = parse_news(FIXTURES / "gnews_sample.xml")
    assert items and items[0].link.startswith("http")


def test_validation_rejects_malformed_market_bar():
    bar = MarketBar(source="test", symbol="BAD", timestamp="2026-01-01T00:00:00Z", open=200, high=100, low=150, close=175, volume=1)
    with pytest.raises(ValueError, match="invalid OHLC"):
        validate_market_bars([bar])

import os
import pytest
import httpx

from backend.ingestion.connectors.alpha_vantage import fetch_quote
from backend.ingestion.connectors.finnhub import fetch_quote as fetch_finnhub
from backend.ingestion.connectors.fred import fetch_series
from backend.ingestion.connectors.gnews import fetch_rss
from backend.ingestion.connectors.sec_edgar import fetch_submissions
from backend.ingestion.connectors.yahoo import fetch_chart


pytestmark = pytest.mark.slow


def test_yahoo_live():
    assert fetch_chart("AAPL")


def test_alpha_vantage_live():
    assert fetch_quote("IBM", os.getenv("ALPHA_VANTAGE_API_KEY", "demo")).symbol == "IBM"


def test_finnhub_live():
    token = os.getenv("FINNHUB_API_KEY")
    if not token:
        pytest.skip("FINNHUB_API_KEY is not configured")
    assert fetch_finnhub("AAPL", token).symbol == "AAPL"


def test_sec_live():
    assert fetch_submissions("320193", os.getenv("SEC_USER_AGENT", "AI-Financial-Advisor contact@example.com"))


def test_fred_live():
    try:
        assert fetch_series("GDP")
    except httpx.HTTPError as exc:
        pytest.skip(f"FRED transport unavailable in this environment: {exc}")


def test_rss_live():
    assert fetch_rss("AAPL")

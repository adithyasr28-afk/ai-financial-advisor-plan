"""Small dependency-light scheduler for the Phase 1 ingestion run."""
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import psycopg
import httpx
from dotenv import load_dotenv

from .connectors.alpha_vantage import parse_fixture as parse_alpha
from .connectors.fred import parse_fixture as parse_fred
from .connectors.gnews import parse_fixture as parse_news
from .connectors.sec_edgar import parse_fixture as parse_sec
from .connectors.yahoo import parse_fixture as parse_yahoo
from .connectors.alpha_vantage import fetch_quote as fetch_alpha
from .connectors.finnhub import fetch_quote as fetch_finnhub
from .connectors.fred import fetch_series
from .connectors.gnews import fetch_rss
from .connectors.sec_edgar import fetch_submissions
from .connectors.yahoo import fetch_chart


def collect_fixture_records(fixtures: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    records.extend(item.model_dump(mode="json") for item in parse_yahoo(fixtures / "yahoo_sample.json"))
    records.append(parse_alpha(fixtures / "alpha_vantage_sample.json").model_dump(mode="json"))
    records.extend(item.model_dump(mode="json") for item in parse_sec(fixtures / "sec_edgar_sample.json")[:5])
    records.extend(item.model_dump(mode="json") for item in parse_fred(fixtures / "fred_sample.csv"))
    records.extend(item.model_dump(mode="json") for item in parse_news(fixtures / "gnews_sample.xml")[:5])
    return records


def collect_live_records(fixtures: Path | None = None) -> list[dict[str, Any]]:
    """Fetch and normalize one live batch from every configured source."""
    records: list[dict[str, Any]] = []
    records.extend(item.model_dump(mode="json") for item in fetch_chart("AAPL"))
    records.append(fetch_alpha("IBM", os.getenv("ALPHA_VANTAGE_API_KEY", "demo")).model_dump(mode="json"))
    token = os.getenv("FINNHUB_API_KEY")
    if not token:
        raise RuntimeError("FINNHUB_API_KEY is required for a complete live ingestion run")
    records.append(fetch_finnhub("AAPL", token).model_dump(mode="json"))
    records.extend(item.model_dump(mode="json") for item in fetch_submissions("320193", os.getenv("SEC_USER_AGENT", "AI-Financial-Advisor contact@example.com"))[:5])
    try:
        records.extend(item.model_dump(mode="json") for item in fetch_series("GDP"))
    except httpx.HTTPError:
        if fixtures is None:
            raise
        logging.warning("FRED live transport failed; using the verified FRED fixture for this run")
        records.extend(item.model_dump(mode="json") for item in parse_fred(fixtures / "fred_sample.csv"))
    records.extend(item.model_dump(mode="json") for item in fetch_rss("AAPL")[:5])
    return records


def run_once(database_url: str, fixtures: Path) -> int:
    records = collect_fixture_records(fixtures)
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS ingestion_records (id BIGSERIAL PRIMARY KEY, source TEXT NOT NULL, payload JSONB NOT NULL, ingested_at TIMESTAMPTZ NOT NULL)")
            for record in records:
                cursor.execute("INSERT INTO ingestion_records (source, payload, ingested_at) VALUES (%s, %s::jsonb, %s)", (record["source"], json.dumps(record), datetime.now(timezone.utc)))
        connection.commit()
    return len(records)


def run_forever(database_url: str, fixtures: Path, interval_seconds: int = 3600) -> None:
    while True:
        run_once(database_url, fixtures)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    load_dotenv(Path(__file__).parents[1] / ".env")
    root = Path(__file__).parents[2]
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_financial_advisor")
    if os.getenv("INGESTION_FIXTURES", "0") == "1":
        count = run_once(database_url, root / "fixtures")
    else:
        records = collect_live_records(root / "fixtures")
        with psycopg.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS ingestion_records (id BIGSERIAL PRIMARY KEY, source TEXT NOT NULL, payload JSONB NOT NULL, ingested_at TIMESTAMPTZ NOT NULL)")
                for record in records:
                    cursor.execute("INSERT INTO ingestion_records (source, payload, ingested_at) VALUES (%s, %s::jsonb, %s)", (record["source"], json.dumps(record), datetime.now(timezone.utc)))
            connection.commit()
        count = len(records)
    print(f"ingested {count} records")

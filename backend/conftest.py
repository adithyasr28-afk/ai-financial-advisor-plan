import os
from pathlib import Path

import psycopg
import pytest

from backend.rag.pipeline import ingest_directory
from backend.rag.store import ensure_schema

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "fixtures" / "annual_reports"


@pytest.fixture(scope="session", autouse=True)
def ensure_rag_chunks_seeded():
    """
    Several agent tests (test_agents.py, test_explainability_schema.py,
    test_financial_statement_agent.py) exercise the financial_statement
    agent, which reads evidence from the rag_chunks table. Nothing else in
    the repo populates that table automatically - it previously required
    someone to manually run `python -m backend.rag.pipeline` first, which
    is never wired into CI. On a fresh checkout / fresh CI Postgres
    container, those tests would fail with "relation rag_chunks does not
    exist" (or return no evidence and fail their assertions).

    This fixture makes that setup a given instead of an assumption: it
    creates the schema if missing and ingests the sample SEC filings if the
    table is empty, once per test session. It's a no-op if the data has
    already been ingested (e.g. running tests repeatedly against the same
    local dev database).
    """
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/ai_financial_advisor",
    )

    try:
        connection = psycopg.connect(database_url)
    except psycopg.OperationalError:
        # No DB reachable in this test environment (e.g. a pure unit-test
        # run with no Postgres available). Don't mask that - let any test
        # that actually needs the DB fail on its own with a clear error,
        # rather than swallowing a real connectivity problem here.
        return

    try:
        ensure_schema(connection)
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM rag_chunks")
            (count,) = cursor.fetchone()
    finally:
        connection.close()

    if count == 0:
        ingest_directory(database_url, FIXTURES_DIR)

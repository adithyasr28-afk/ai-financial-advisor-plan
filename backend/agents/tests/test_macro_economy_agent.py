import pytest
from pathlib import Path
from backend.agents.system import AgentContext, macro_economy
from backend.agents.schemas import Stance


@pytest.fixture
def context():
    return AgentContext.from_project()


def test_macro_economy_returns_real_fred_observation(context):
    result = macro_economy(context, "What is the current GDP?")
    assert result.agent == "macro_economy"
    assert result.evidence
    assert len(result.evidence) == 1
    assert result.evidence[0].source == "fred"
    assert result.evidence[0].series_id == "GDP"
    assert result.evidence[0].observation_date is not None
    assert result.evidence[0].value is not None
    assert result.confidence == 0.8
    assert result.stance is None


def test_macro_economy_summary_mentions_verified_observation(context):
    result = macro_economy(context, "inflation data")
    assert result.agent == "macro_economy"
    assert "verified" in result.summary.lower()
    assert "fred" in result.summary.lower()


def test_macro_economy_uses_fixture_data(context):
    result = macro_economy(context, "any query")
    assert result.agent == "macro_economy"
    assert result.evidence[0].series_id == "GDP"
    assert result.evidence[0].observation_date == "2026-01-01"
    assert result.evidence[0].value == 31865.721
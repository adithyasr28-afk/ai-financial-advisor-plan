import pytest
from pathlib import Path
from backend.agents.system import AgentContext, valuation
from backend.agents.schemas import Stance


@pytest.fixture
def context():
    return AgentContext.from_project()


def test_valuation_returns_real_alpha_vantage_quote(context):
    result = valuation(context, "What is the valuation of IBM?")
    assert result.agent == "valuation"
    assert result.evidence
    assert len(result.evidence) == 1
    assert result.evidence[0].source == "alpha_vantage"
    assert result.evidence[0].symbol == "IBM"
    assert result.evidence[0].price is not None
    assert result.evidence[0].price > 0
    assert result.confidence == 0.7
    assert result.stance == Stance.NEUTRAL


def test_valuation_summary_mentions_market_evidence_not_fair_value(context):
    result = valuation(context, "fair value of Apple")
    assert result.agent == "valuation"
    assert "market evidence" in result.summary.lower()
    assert "not a fair-value estimate" in result.summary.lower() or "fair-value" in result.summary.lower()


def test_valuation_uses_fixture_data(context):
    result = valuation(context, "any query")
    assert result.agent == "valuation"
    assert result.evidence[0].trading_day == "2026-07-28"
    assert result.evidence[0].price == 227.55
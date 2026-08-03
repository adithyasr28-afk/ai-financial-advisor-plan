import pytest
from pathlib import Path
from backend.agents.system import AgentContext, portfolio
from backend.agents.schemas import Stance


@pytest.fixture
def context():
    return AgentContext.from_project()


def test_portfolio_returns_real_market_mark(context):
    result = portfolio(context, "What are my portfolio holdings?")
    assert result.agent == "portfolio"
    assert result.evidence
    assert len(result.evidence) == 1
    assert result.evidence[0].source == "yahoo_finance"
    assert result.evidence[0].symbol == "AAPL"
    assert result.evidence[0].price is not None
    assert result.evidence[0].price > 0
    assert result.confidence == 0.5
    assert result.stance == Stance.INSUFFICIENT_DATA


def test_portfolio_summary_mentions_holdings_not_supplied(context):
    result = portfolio(context, "portfolio allocation")
    assert result.agent == "portfolio"
    assert "holdings" in result.summary.lower()
    assert "not supplied" in result.summary.lower() or "were not supplied" in result.summary.lower()


def test_portfolio_uses_fixture_data(context):
    result = portfolio(context, "any query")
    assert result.agent == "portfolio"
    assert result.evidence[0].price == 341.3399963378906
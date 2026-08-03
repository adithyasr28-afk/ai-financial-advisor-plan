import pytest
from pathlib import Path
from backend.agents.system import AgentContext, technical_analysis
from backend.agents.schemas import Stance


@pytest.fixture
def context():
    return AgentContext.from_project()


def test_technical_analysis_returns_real_yahoo_bars(context):
    result = technical_analysis(context, "What is the trend for AAPL?")
    assert result.agent == "technical_analysis"
    assert result.evidence
    assert len(result.evidence) == 1
    assert result.evidence[0].source == "yahoo_finance"
    assert result.evidence[0].symbol == "AAPL"
    assert result.evidence[0].first_close is not None
    assert result.evidence[0].last_close is not None
    assert result.confidence == 0.6


def test_technical_analysis_stance_reflects_price_change(context):
    result = technical_analysis(context, "trend analysis")
    assert result.agent == "technical_analysis"
    assert result.stance in [Stance.UPTREND, Stance.DOWNTREND]
    first_close = result.evidence[0].first_close
    last_close = result.evidence[0].last_close
    change = last_close / first_close - 1
    if change > 0:
        assert result.stance == Stance.UPTREND
    else:
        assert result.stance == Stance.DOWNTREND


def test_technical_analysis_uses_fixture_data(context):
    result = technical_analysis(context, "any query")
    assert result.agent == "technical_analysis"
    assert result.evidence[0].first_close == 321.6600036621094
    assert result.evidence[0].last_close == 341.3399963378906
    assert "6.12%" in result.summary or "moved" in result.summary.lower()
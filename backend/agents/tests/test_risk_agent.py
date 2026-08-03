import pytest
from pathlib import Path
from backend.agents.system import AgentContext, risk
from backend.agents.schemas import Stance


@pytest.fixture
def context():
    return AgentContext.from_project()


def test_risk_returns_real_model_metrics(context):
    result = risk(context, "What is the portfolio risk?")
    assert result.agent == "risk"
    assert result.evidence
    assert len(result.evidence) == 1
    assert result.evidence[0].source == "models/risk_prediction/metrics.json"
    assert result.evidence[0].metrics is not None
    assert result.confidence == 0.4
    assert result.stance == Stance.HOLD


def test_risk_reports_insufficient_test_sample(context):
    result = risk(context, "risk assessment")
    assert result.agent == "risk"
    metrics = result.evidence[0].metrics
    assert metrics["sample_count"] == 3
    assert metrics["target"]["f1"] == 0.0
    assert "too small" in metrics["ship_decision"] or "too few" in metrics["ship_decision"]


def test_risk_summary_mentions_model_artifact_available(context):
    result = risk(context, "volatility risk")
    assert result.agent == "risk"
    assert "artifact" in result.summary.lower() or "model" in result.summary.lower()
    assert "too small" in result.summary.lower() or "insufficient" in result.summary.lower()
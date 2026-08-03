import pytest
from pathlib import Path
from backend.agents.system import AgentContext, report_writer
from backend.agents.schemas import AgentResponse, EvidenceItem, Stance


@pytest.fixture
def context():
    return AgentContext.from_project()


def test_report_writer_aggregates_all_specialist_results(context):
    results = [
        AgentResponse(agent="news_intelligence", query="q", summary="news summary", evidence=[EvidenceItem(source="rss", title="Test")], stance=None, confidence=0.8),
        AgentResponse(agent="financial_statement", query="q", summary="filing summary", evidence=[EvidenceItem(chunk_id="test:1", source_file="test.htm", source="sec_filing")], confidence=0.6),
        AgentResponse(agent="valuation", query="q", summary="valuation summary", evidence=[EvidenceItem(source="alpha_vantage", price=100)], stance=Stance.NEUTRAL, confidence=0.7),
        AgentResponse(agent="risk", query="q", summary="risk summary", evidence=[EvidenceItem(source="model", metrics={})], stance=Stance.HOLD, confidence=0.4),
        AgentResponse(agent="technical_analysis", query="q", summary="tech summary", evidence=[EvidenceItem(source="yahoo_finance", first_close=100, last_close=110)], stance=Stance.UPTREND, confidence=0.6),
        AgentResponse(agent="portfolio", query="q", summary="portfolio summary", evidence=[EvidenceItem(source="yahoo_finance", price=110)], stance=Stance.INSUFFICIENT_DATA, confidence=0.5),
        AgentResponse(agent="macro_economy", query="q", summary="macro summary", evidence=[EvidenceItem(source="fred", value=1000)], confidence=0.8),
    ]
    result = report_writer(context, "comprehensive report", results)
    assert result.agent == "report_writer"
    assert result.evidence
    assert len(result.evidence) == sum(len(r.evidence) for r in results)
    assert result.stance == Stance.CONFLICT
    assert result.confidence == 0.4
    assert "7 specialist results" in result.summary or "Combined" in result.summary


def test_report_writer_stance_conflict_when_stances_differ(context):
    results = [
        AgentResponse(agent="a1", query="q", summary="s1", evidence=[], stance=Stance.BULLISH, confidence=0.5),
        AgentResponse(agent="a2", query="q", summary="s2", evidence=[], stance=Stance.BEARISH, confidence=0.5),
    ]
    result = report_writer(context, "q", results)
    assert result.stance == Stance.CONFLICT


def test_report_writer_stance_agreed_when_all_same(context):
    results = [
        AgentResponse(agent="a1", query="q", summary="s1", evidence=[], stance=Stance.BULLISH, confidence=0.5),
        AgentResponse(agent="a2", query="q", summary="s2", evidence=[], stance=Stance.BULLISH, confidence=0.5),
    ]
    result = report_writer(context, "q", results)
    assert result.stance == Stance.BULLISH


def test_report_writer_confidence_is_min_of_specialists(context):
    results = [
        AgentResponse(agent="a1", query="q", summary="s1", evidence=[], confidence=0.9),
        AgentResponse(agent="a2", query="q", summary="s2", evidence=[], confidence=0.5),
        AgentResponse(agent="a3", query="q", summary="s3", evidence=[], confidence=0.7),
    ]
    result = report_writer(context, "q", results)
    assert result.confidence == 0.5
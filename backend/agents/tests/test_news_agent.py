import pytest
from pathlib import Path
from backend.agents.system import AgentContext, news_intelligence
from backend.agents.schemas import Stance


@pytest.fixture
def context():
    return AgentContext.from_project()


def test_news_intelligence_filters_by_entity(context):
    # Query for Apple news
    result = news_intelligence(context, "What is the latest news for Apple?")
    assert result.agent == "news_intelligence"
    # The gnews_sample.xml contains Apple-related headlines
    assert any("Apple" in item.title or "AAPL" in item.title for item in result.evidence if item.title)
    assert result.stance in [Stance.BULLISH, Stance.BEARISH, Stance.NEUTRAL]
    assert result.evidence[0].entities is not None


def test_news_intelligence_sentiment_integration(context):
    result = news_intelligence(context, "market news")
    # Check that sentiment scores are present in evidence
    for item in result.evidence:
        assert item.sentiment_score is not None
        assert item.sentiment_score in [-1, 0, 1]
    
    # Check aggregated stance
    if result.stance == Stance.BULLISH:
        assert sum(item.sentiment_score for item in result.evidence if item.sentiment_score is not None) > 0
    elif result.stance == Stance.BEARISH:
        assert sum(item.sentiment_score for item in result.evidence if item.sentiment_score is not None) < 0
    else:
        assert sum(item.sentiment_score for item in result.evidence if item.sentiment_score is not None) == 0
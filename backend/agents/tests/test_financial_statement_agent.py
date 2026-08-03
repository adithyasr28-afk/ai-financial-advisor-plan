import pytest
from pathlib import Path
from backend.agents.system import AgentContext, financial_statement
from backend.agents.schemas import Stance


@pytest.fixture
def context():
    return AgentContext.from_project()


def test_financial_statement_retrieves_real_filing_chunks(context):
    result = financial_statement(context, "What was Apple's net sales in 2025?")
    assert result.agent == "financial_statement"
    assert result.evidence
    assert len(result.evidence) >= 1
    assert result.evidence[0].chunk_id is not None
    assert result.evidence[0].source_file is not None
    assert result.evidence[0].excerpt is not None
    assert result.confidence > 0


def test_financial_statement_lower_confidence_for_irrelevant_query(context):
    result = financial_statement(context, "What is the meaning of life according to Apple filings?")
    assert result.agent == "financial_statement"
    assert result.evidence
    assert result.confidence < 0.5
    assert "retrieved" in result.summary.lower()


def test_financial_statement_confidence_based_on_retrieval_similarity(context):
    result = financial_statement(context, "Apple revenue")
    assert result.agent == "financial_statement"
    assert 0.0 <= result.confidence <= 1.0
    if result.evidence:
        assert result.confidence > 0.0
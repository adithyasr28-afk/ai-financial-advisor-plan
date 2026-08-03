from backend.agents.system import AgentContext, AGENTS, orchestrate, report_writer, route
from backend.agents.schemas import AgentResponse, Stance


def test_routing_covers_distinct_query_types():
    assert route("latest news headlines") == ["news_intelligence"]
    assert route("what is the company revenue in the 10-K") == ["financial_statement"]
    assert "risk" in route("portfolio risk and volatility")


def test_all_eight_agents_run_against_real_state():
    context = AgentContext.from_project()
    for name, agent in AGENTS.items():
        result = agent(context, name)
        assert result.agent == name
        assert result.evidence
    report = orchestrate(context, "comprehensive report")
    assert len(report["results"]) == 8


def test_conflict_resolution_surfaces_disagreement():
    context = AgentContext.from_project()
    results = [
        AgentResponse(agent="technical_analysis", query="q", summary="up", evidence=[], stance=Stance.UPTREND, confidence=0.6),
        AgentResponse(agent="risk", query="q", summary="hold", evidence=[], stance=Stance.HOLD, confidence=0.4),
    ]
    report = report_writer(context, "q", results)
    assert report.stance == Stance.CONFLICT
    resolved = orchestrate(context, "comprehensive report")
    assert "disagreements" in resolved
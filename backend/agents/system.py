from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

import joblib
from dotenv import load_dotenv

from backend.ingestion.connectors.alpha_vantage import parse_fixture as parse_alpha
from backend.ingestion.connectors.fred import parse_fixture as parse_fred
from backend.ingestion.connectors.gnews import parse_fixture as parse_news
from backend.ingestion.connectors.yahoo import parse_fixture as parse_yahoo
from backend.rag.pipeline import cited_answer
from .schemas import AgentResponse, EvidenceItem, Stance


class AgentContext:
    root: Path
    database_url: str

    def __init__(self, root: Path, database_url: str):
        self.root = root
        self.database_url = database_url

    @classmethod
    def from_project(cls, root: Path | None = None) -> "AgentContext":
        project = root or Path(__file__).parents[2]
        load_dotenv(project / "backend" / ".env")
        return cls(project, os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_financial_advisor"))


def _entities(text: str) -> set[str]:
    known = {"apple", "nvidia", "tesla", "qualcomm", "ford", "coca-cola", "samsung", "vti", "china"}
    lowered = text.lower()
    return {entity for entity in known if entity in lowered}


def _compute_confidence_from_sentiment(evidence: list[EvidenceItem]) -> float:
    if not evidence:
        return 0.5
    scores = [e.sentiment_score for e in evidence if e.sentiment_score is not None]
    if not scores:
        return 0.5
    avg = sum(scores) / len(scores)
    return min(1.0, max(0.0, 0.5 + avg * 0.3))


def news_intelligence(context: AgentContext, query: str) -> AgentResponse:
    items = parse_news(context.root / "fixtures" / "gnews_sample.xml")
    query_entities = _entities(query)
    if query_entities:
        items = [item for item in items if _entities(item.title) & query_entities]
    
    if not items:
        items = parse_news(context.root / "fixtures" / "gnews_sample.xml")[:5]
    else:
        items = items[:5]
        
    model_path = context.root / "models" / "sentiment" / "model.joblib"
    evidence = []
    if model_path.exists():
        model = joblib.load(model_path)
        predictions = model.predict([item.title for item in items])
        for item, pred in zip(items, predictions, strict=True):
            evidence.append(EvidenceItem(
                source=item.source,
                title=item.title,
                link=item.link,
                sentiment_score=int(pred),
                entities=list(_entities(item.title))
            ))
    else:
        for item in items:
            evidence.append(EvidenceItem(
                source=item.source,
                title=item.title,
                link=item.link,
                sentiment_score=0,
                entities=list(_entities(item.title))
            ))

    total_sentiment = sum(e.sentiment_score for e in evidence if e.sentiment_score is not None)
    stance = Stance.BULLISH if total_sentiment > 0 else Stance.BEARISH if total_sentiment < 0 else Stance.NEUTRAL
    confidence = _compute_confidence_from_sentiment(evidence)
    
    return AgentResponse(
        agent="news_intelligence",
        query=query,
        summary=f"Analyzed {len(evidence)} headlines. Filtered for: {list(query_entities) or 'market-wide'}.",
        evidence=evidence,
        stance=stance,
        confidence=confidence,
        sources=["rss"],
        assumptions=["Sentiment model trained on financial headlines generalizes to current news"],
        limitations=["Sentiment model trained on limited labeled data; not production-ready"]
    )


def financial_statement(context: AgentContext, query: str) -> AgentResponse:
    answer = cited_answer(context.database_url, query or "net sales", 3)
    if answer["refused"]:
        return AgentResponse(
            agent="financial_statement",
            query=query,
            summary="No filing chunk supports this question.",
            evidence=[],
            stance=None,
            confidence=0.0,
            sources=[],
            assumptions=[],
            limitations=["Retrieval limited to ingested SEC filings; may miss relevant sections"]
        )
    
    evidence = [
        EvidenceItem(
            chunk_id=citation["chunk_id"],
            source_file=citation["source_file"],
            excerpt=excerpt[:300],
            source=citation.get("source_file", "sec_filing")
        )
        for citation, excerpt in zip(answer["citations"], answer["evidence"], strict=True)
    ]
    confidence = min(1.0, max(0.0, answer["citations"][0]["similarity"]))
    
    return AgentResponse(
        agent="financial_statement",
        query=query,
        summary="Retrieved filing evidence for the financial-statement question.",
        evidence=evidence,
        stance=None,
        confidence=confidence,
        sources=["sec_filing"],
        assumptions=["Filing chunks accurately represent the company's financial position"],
        limitations=["Only 3 annual reports ingested; retrieval may miss context across sections"]
    )


def valuation(context: AgentContext, query: str) -> AgentResponse:
    quote = parse_alpha(context.root / "fixtures" / "alpha_vantage_sample.json")
    evidence = [EvidenceItem(
        source=quote.source,
        symbol=quote.symbol,
        trading_day=quote.trading_day.isoformat(),
        price=quote.price
    )]
    
    return AgentResponse(
        agent="valuation",
        query=query,
        summary=f"The verified Alpha Vantage quote for {quote.symbol} is {quote.price:.2f} USD; this is market evidence, not a fair-value estimate.",
        evidence=evidence,
        stance=Stance.NEUTRAL,
        confidence=0.7,
        sources=["alpha_vantage"],
        assumptions=["Current market price reflects available information"],
        limitations=["Single quote snapshot; no DCF, comparables, or intrinsic valuation performed"]
    )


def risk(context: AgentContext, query: str) -> AgentResponse:
    metrics = json.loads((context.root / "models" / "risk_prediction" / "metrics.json").read_text(encoding="utf-8"))
    evidence = [EvidenceItem(
        source="models/risk_prediction/metrics.json",
        metrics=metrics
    )]
    
    return AgentResponse(
        agent="risk",
        query=query,
        summary="Risk model artifact is available, but its measured test sample is too small for production use.",
        evidence=evidence,
        stance=Stance.HOLD,
        confidence=0.4,
        sources=["ml_model"],
        assumptions=["Historical risk patterns persist; model features capture relevant risk factors"],
        limitations=["Test sample size of 3; F1=0.0; not suitable for production decisions"]
    )


def technical_analysis(context: AgentContext, query: str) -> AgentResponse:
    bars = parse_yahoo(context.root / "fixtures" / "yahoo_sample.json")
    change = bars[-1].close / bars[0].close - 1
    stance = Stance.UPTREND if change > 0 else Stance.DOWNTREND
    evidence = [EvidenceItem(
        source=bars[-1].source,
        symbol=bars[-1].symbol,
        first_close=bars[0].close,
        last_close=bars[-1].close
    )]
    
    return AgentResponse(
        agent="technical_analysis",
        query=query,
        summary=f"{bars[0].symbol} moved {change:.2%} across the verified {len(bars)}-bar sample.",
        evidence=evidence,
        stance=stance,
        confidence=0.6,
        sources=["yahoo_finance"],
        assumptions=["Price trend in sample period indicates near-term direction"],
        limitations=["Only 5 bars in fixture; no volume, indicators, or multi-timeframe analysis"]
    )


def portfolio(context: AgentContext, query: str) -> AgentResponse:
    bars = parse_yahoo(context.root / "fixtures" / "yahoo_sample.json")
    evidence = [EvidenceItem(
        source=bars[-1].source,
        symbol=bars[-1].symbol,
        price=bars[-1].close
    )]
    
    return AgentResponse(
        agent="portfolio",
        query=query,
        summary=f"Portfolio context contains a verified {bars[-1].symbol} market mark of {bars[-1].close:.2f} USD; holdings and weights were not supplied.",
        evidence=evidence,
        stance=Stance.INSUFFICIENT_DATA,
        confidence=0.5,
        sources=["yahoo_finance"],
        assumptions=["Market mark reflects current valuation of held securities"],
        limitations=["No holdings, weights, or cost basis provided; cannot compute portfolio metrics"]
    )


def macro_economy(context: AgentContext, query: str) -> AgentResponse:
    observations = parse_fred(context.root / "fixtures" / "fred_sample.csv")
    latest = observations[-1]
    evidence = [EvidenceItem(
        source=latest.source,
        series_id=latest.series_id,
        observation_date=latest.observation_date.isoformat(),
        value=latest.value
    )]
    
    return AgentResponse(
        agent="macro_economy",
        query=query,
        summary=f"The verified FRED {latest.series_id} observation is {latest.value:.3f} on {latest.observation_date}.",
        evidence=evidence,
        stance=None,
        confidence=0.8,
        sources=["fred"],
        assumptions=["FRED series accurately represents the macroeconomic indicator"],
        limitations=["Single series observation; no trend, forecast, or cross-indicator analysis"]
    )


def report_writer(context: AgentContext, query: str, results: list[AgentResponse]) -> AgentResponse:
    evidence = [item for result in results for item in result.evidence]
    stances = {result.stance for result in results if result.stance}
    all_sources = []
    all_assumptions = []
    all_limitations = []
    for result in results:
        all_sources.extend(result.sources)
        all_assumptions.extend(result.assumptions)
        all_limitations.extend(result.limitations)
    
    return AgentResponse(
        agent="report_writer",
        query=query,
        summary=f"Combined {len(results)} specialist results; disagreements are preserved for review.",
        evidence=evidence,
        stance=Stance.CONFLICT if len(stances) > 1 else (next(iter(stances)) if stances else None),
        confidence=min((result.confidence for result in results), default=0.0),
        sources=list(set(all_sources)),
        assumptions=list(set(all_assumptions)),
        limitations=list(set(all_limitations))
    )


AGENTS = {
    "news_intelligence": news_intelligence,
    "financial_statement": financial_statement,
    "valuation": valuation,
    "risk": risk,
    "technical_analysis": technical_analysis,
    "portfolio": portfolio,
    "macro_economy": macro_economy
}


def route(query: str) -> list[str]:
    lowered = query.lower()
    if any(word in lowered for word in ("report", "comprehensive", "full analysis")):
        return list(AGENTS) + ["report_writer"]
    selected = []
    rules = {
        "news_intelligence": ("news", "headline"),
        "financial_statement": ("revenue", "10-k", "filing", "statement", "net sales"),
        "valuation": ("valuation", "fair value", "price"),
        "risk": ("risk", "volatility"),
        "technical_analysis": ("technical", "trend", "moving average"),
        "portfolio": ("portfolio", "holding", "allocation"),
        "macro_economy": ("macro", "gdp", "economy", "inflation"),
    }
    for name, words in rules.items():
        if any(word in lowered for word in words):
            selected.append(name)
    return selected or ["financial_statement"]


def orchestrate(context: AgentContext, query: str) -> dict[str, Any]:
    selected = route(query)
    results: list[AgentResponse] = []
    for name in selected:
        if name == "report_writer":
            results.append(report_writer(context, query, results))
        else:
            results.append(AGENTS[name](context, query))
    stances = {result.stance for result in results if result.stance and result.agent != "report_writer"}
    return {
        "query": query,
        "agents": selected,
        "results": [result.model_dump() for result in results],
        "disagreements": [{"stances": sorted([s.value for s in stances]), "message": "Specialists disagree; no stance was silently discarded."}] if len(stances) > 1 else []
    }
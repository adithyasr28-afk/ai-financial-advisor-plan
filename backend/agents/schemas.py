from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime, timezone
from enum import Enum


class Stance(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    HOLD = "hold"
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    INSUFFICIENT_DATA = "insufficient_data"
    CONFLICT = "conflict"


class EvidenceItem(BaseModel):
    source: str
    chunk_id: str | None = None
    source_file: str | None = None
    title: str | None = None
    link: str | None = None
    symbol: str | None = None
    price: float | None = None
    trading_day: str | None = None
    first_close: float | None = None
    last_close: float | None = None
    series_id: str | None = None
    observation_date: str | None = None
    value: float | None = None
    sentiment_score: int | None = None
    entities: list[str] | None = None
    excerpt: str | None = None
    metrics: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    agent: str
    query: str
    summary: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    stance: Stance | None = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def model_post_init(self, __context: Any) -> None:
        if not self.sources and self.evidence:
            self.sources = list({e.source for e in self.evidence if e.source})

    def evidence_as_dict(self) -> list[dict[str, Any]]:
        return [e.model_dump(exclude_none=True) for e in self.evidence]
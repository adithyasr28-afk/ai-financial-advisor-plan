from datetime import date, datetime
from pydantic import BaseModel, Field


class MarketBar(BaseModel):
    source: str
    symbol: str
    timestamp: datetime
    open: float = Field(ge=0)
    high: float = Field(ge=0)
    low: float = Field(ge=0)
    close: float = Field(ge=0)
    volume: int = Field(ge=0)


class Quote(BaseModel):
    source: str
    symbol: str
    price: float = Field(gt=0)
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    volume: int = Field(ge=0)
    trading_day: date


class Filing(BaseModel):
    source: str
    cik: str
    accession_number: str
    form: str
    filing_date: date
    primary_document: str


class MacroObservation(BaseModel):
    source: str
    series_id: str
    observation_date: date
    value: float


class NewsItem(BaseModel):
    source: str
    title: str
    link: str
    published_at: datetime | None = None
    summary: str | None = None

from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import time
import sys
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Ensure backend module is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.agents.system import AgentContext, orchestrate

app = FastAPI(title="AI Financial Advisor API", version="0.1.0")

# The frontend runs in the browser as a separate origin (different port, or a
# different host entirely once deployed), so without this every fetch() call
# from app/**/page.tsx is silently blocked by the browser's CORS policy -
# it looks like "can't reach the backend" even though the server is fine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
ORCHESTRATION_COUNT = Counter("orchestration_total", "Total orchestrations", ["query_type"])
ORCHESTRATION_LATENCY = Histogram("orchestration_duration_seconds", "Orchestration latency")
AGENT_CONFIDENCE = Gauge("agent_confidence", "Agent confidence score", ["agent"])
ACTIVE_CONNECTIONS = Gauge("active_connections", "Active connections")


class OrchestrateRequest(BaseModel):
    query: str


class OrchestrateResponse(BaseModel):
    query: str
    agents: list[str]
    results: list[dict[str, Any]]
    disagreements: list[dict[str, Any]]


@app.middleware("http")
async def prometheus_middleware(request, call_next):
    start = time.time()
    ACTIVE_CONNECTIONS.inc()
    try:
        response = await call_next(request)
        duration = time.time() - start
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(duration)
        return response
    finally:
        ACTIVE_CONNECTIONS.dec()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/orchestrate", response_model=OrchestrateResponse)
def orchestrate_endpoint(request: OrchestrateRequest) -> OrchestrateResponse:
    start = time.time()
    context = AgentContext.from_project()
    result = orchestrate(context, request.query)
    duration = time.time() - start

    # Record metrics
    ORCHESTRATION_COUNT.labels(query_type=request.query.split()[0] if request.query else "unknown").inc()
    ORCHESTRATION_LATENCY.observe(duration)
    for agent_result in result["results"]:
        AGENT_CONFIDENCE.labels(agent=agent_result["agent"]).set(agent_result["confidence"])

    return OrchestrateResponse(**result)


@app.get("/api/v1/agents")
def list_agents() -> dict[str, list[str]]:
    from backend.agents.system import AGENTS
    return {"agents": list(AGENTS.keys()) + ["report_writer"]}


@app.get("/api/v1/market-data/{symbol}")
def get_market_data(symbol: str) -> dict[str, Any]:
    from backend.ingestion.connectors import yahoo
    from backend.ingestion.live import cached

    symbol = symbol.upper()

    try:
        bars = cached(f"bars:{symbol}", ttl_seconds=60, fetch=lambda: yahoo.fetch_chart(symbol, range_="3mo", interval="1d"))
        live = True
    except Exception:
        bars = []
        live = False

    if not bars:
        # No live data (offline, rate-limited, or an invalid symbol) - the
        # bundled fixture only ever covers one demo symbol.
        context = AgentContext.from_project()
        fixture_bars = yahoo.parse_fixture(context.root / "fixtures" / "yahoo_sample.json")
        if fixture_bars and fixture_bars[0].symbol.upper() == symbol:
            bars = fixture_bars
            live = False
        else:
            return {
                "error": "Couldn't fetch live data for this symbol and no offline fixture is available for it",
                "symbol": symbol,
            }

    return {
        "symbol": symbol,
        "price": bars[-1].close,
        "change_pct": (bars[-1].close / bars[0].close - 1) * 100,
        "bars": [{"close": b.close, "date": b.timestamp.date().isoformat()} for b in bars],
        "live": live,
    }


@app.get("/api/v1/news")
def get_news(limit: int = Query(10, le=50), symbol: str | None = None) -> dict[str, Any]:
    from datetime import datetime, timezone
    from backend.ingestion.connectors import gnews
    from backend.ingestion.live import cached

    symbols = [symbol.upper()] if symbol else ["AAPL", "MSFT", "SPY"]

    def fetch_live():
        seen: set[str] = set()
        merged = []
        for sym in symbols:
            for item in gnews.fetch_rss(sym):
                if item.link not in seen:
                    seen.add(item.link)
                    merged.append(item)
        merged.sort(key=lambda i: i.published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return merged

    try:
        items = cached(f"news:{','.join(symbols)}", ttl_seconds=300, fetch=fetch_live)
        live = True
    except Exception:
        context = AgentContext.from_project()
        items = gnews.parse_fixture(context.root / "fixtures" / "gnews_sample.xml")
        live = False

    return {
        "articles": [
            {
                "title": item.title,
                "link": item.link,
                "source": item.source,
                "published": item.published_at.isoformat() if item.published_at else None,
            }
            for item in items[:limit]
        ],
        "live": live,
    }


@app.get("/api/v1/macro/{series_id}")
def get_macro(series_id: str) -> dict[str, Any]:
    from backend.ingestion.connectors import fred
    from backend.ingestion.live import cached

    series_id = series_id.upper()

    try:
        observations = cached(f"macro:{series_id}", ttl_seconds=3600, fetch=lambda: fred.fetch_series(series_id))
        live = True
    except Exception:
        observations = []
        live = False

    if not observations:
        context = AgentContext.from_project()
        fixture_obs = fred.parse_fixture(context.root / "fixtures" / "fred_sample.csv")
        if fixture_obs and fixture_obs[-1].series_id == series_id:
            observations = fixture_obs
            live = False
        else:
            return {"error": "Series not found", "series_id": series_id}

    latest = observations[-1]
    return {
        "series_id": latest.series_id,
        "value": latest.value,
        "observation_date": latest.observation_date.isoformat(),
        "source": latest.source,
        "live": live,
    }


class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    start_date: str
    end_date: str


@app.post("/api/v1/backtest")
def run_backtest_endpoint(request: BacktestRequest) -> dict[str, Any]:
    from datetime import date as date_cls
    from backend.ingestion.connectors import yahoo
    from backend.backtesting.engine import run_backtest, STRATEGIES

    if request.strategy not in STRATEGIES:
        return {"error": f"Unknown strategy '{request.strategy}'. Choose one of: {', '.join(STRATEGIES)}"}

    try:
        start = date_cls.fromisoformat(request.start_date)
        end = date_cls.fromisoformat(request.end_date)
    except ValueError:
        return {"error": "start_date and end_date must be in YYYY-MM-DD format"}

    if start >= end:
        return {"error": "start_date must be before end_date"}

    symbol = request.symbol.upper()
    try:
        bars = yahoo.fetch_chart_range(symbol, start, end)
    except Exception as exc:
        return {"error": f"Couldn't fetch historical data for {symbol}: {exc}"}

    if len(bars) < 2:
        return {"error": f"Not enough historical data returned for {symbol} in that date range"}

    closes = [b.close for b in bars]
    dates = [b.timestamp.date().isoformat() for b in bars]
    metrics = run_backtest(closes, request.strategy)

    return {
        "symbol": symbol,
        "strategy": request.strategy,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "total_return_pct": metrics.total_return_pct,
        "annualized_return_pct": metrics.annualized_return_pct,
        "max_drawdown_pct": metrics.max_drawdown_pct,
        "sharpe_ratio": metrics.sharpe_ratio,
        "trades": metrics.trades,
        "win_rate_pct": metrics.win_rate_pct,
        "equity_curve": metrics.equity_curve,
        "dates": dates,
    }
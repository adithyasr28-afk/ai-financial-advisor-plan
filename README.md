# AI Financial Advisor

An explainable, multi-agent financial research assistant. Ask a question such as *"AAPL comprehensive report"* and a router sends it to specialist agents (news, filings, valuation, risk, technicals, portfolio, macro). Each returns **evidence, a stance, a confidence score, assumptions and limitations** in one shared schema. When the specialists disagree, the disagreement is surfaced instead of being averaged away.

The repo contains a FastAPI backend, a Next.js dashboard, a Postgres/pgvector RAG layer over Apple's SEC 10-K filings, a small backtesting engine, an evaluation harness, and a monitoring and CI setup.

> **Status: working prototype, built phase by phase.** [`plan.md`](plan.md) is the *full* product vision (double-entry accounting, tax engine, CFA-grade portfolio analytics, auth, an LLM layer). Only the research-and-analysis slice is implemented. See [What is and isn't built](#what-is-and-isnt-built) so you know what to expect.

---

## Contents

- [Features](#features)
- [How it works](#how-it-works)
- [What is and isn't built](#what-is-and-isnt-built)
- [Tech stack](#tech-stack)
- [Repository layout](#repository-layout)
- [Getting started](#getting-started)
- [API reference](#api-reference)
- [Data and models](#data-and-models)
- [Evaluation results](#evaluation-results)
- [Testing and CI](#testing-and-ci)
- [Monitoring](#monitoring)
- [Known issues and limitations](#known-issues-and-limitations)
- [Documentation map](#documentation-map)

---

## Features

| Area | What you get |
|---|---|
| **Multi-agent analysis** | Seven specialists (`news_intelligence`, `financial_statement`, `valuation`, `risk`, `technical_analysis`, `portfolio`, `macro_economy`) plus a `report_writer` that merges them. A keyword router picks which ones run for a query. |
| **Explainability by contract** | Every agent returns an `AgentResponse` (Pydantic): `summary`, `evidence[]`, `stance`, `confidence` (0–1), `sources`, `assumptions`, `limitations`. Tests fail if a required field is missing or empty. |
| **Conflict surfacing** | If agents hold different stances (e.g. bullish vs. hold), the response lists a `disagreements` entry and the report writer's stance becomes `conflict`. |
| **Finance RAG** | Three Apple 10-K filings (2023–2025) are chunked and stored in Postgres with pgvector. Answers are **retrieval evidence with citations** (`chunk_id`, `source_file`, similarity). If nothing is retrieved, the system refuses to answer. |
| **Data ingestion** | Connectors for Yahoo Finance, Alpha Vantage, Finnhub, SEC EDGAR, FRED and Google News RSS, with schema validation (e.g. malformed OHLC rows are rejected) and a scheduler that writes to Postgres. |
| **Data engineering** | Cleaning (missing rows, split adjustment, currency and timestamp normalization, holiday gaps), return/volatility/ratio features, and SHA-256 content-addressed dataset manifests under `data_versions/`. |
| **Classical ML benchmarks** | Forecasting, sentiment, anomaly detection, company similarity and risk prediction, trained with a leakage-safe chronological 60/20/20 split. Each model records its metrics and a ship/hold decision. |
| **Backtesting** | Four strategies (`buy_hold`, `sma_crossover`, `rsi_mean_reversion`, `macd`) with total/annualized return, max drawdown, Sharpe, trade count, win rate and equity curve. |
| **Dashboard** | Next.js 14 app with Dashboard, Company Analysis, Portfolio, News, Watchlists, AI Chat, Alerts and Backtesting pages. |
| **Observability and CI** | Prometheus metrics at `/metrics`, a Grafana dashboard, and a GitHub Actions pipeline. |

---

## How it works

```mermaid
flowchart LR
  User --> FE["Next.js dashboard<br/>(frontend/)"]
  FE -->|REST /api/v1/*| API["FastAPI<br/>(backend/main.py)"]

  API --> ORCH["Orchestrator<br/>route() → specialists"]
  ORCH --> A1[news_intelligence]
  ORCH --> A2[financial_statement]
  ORCH --> A3[valuation]
  ORCH --> A4[risk]
  ORCH --> A5[technical_analysis]
  ORCH --> A6[portfolio]
  ORCH --> A7[macro_economy]
  A1 & A2 & A3 & A4 & A5 & A6 & A7 --> RW["report_writer<br/>(merge + conflict check)"]

  A2 --> RAG["RAG: cited_answer()"] --> PG[("PostgreSQL + pgvector<br/>rag_chunks")]
  A1 --> SENT["sentiment model<br/>(models/)"]
  A3 & A5 & A6 & A7 --> FIX["fixtures/<br/>Alpha Vantage, Yahoo, FRED"]

  API --> LIVE["Live endpoints with fixture fallback<br/>market-data · news · macro"]
  API --> BT["Backtest engine"]
  API --> PROM["/metrics → Prometheus → Grafana"]
```

1. The frontend posts a query to `POST /api/v1/orchestrate`.
2. `route()` picks specialists by keyword. Words like *news*, *revenue*, *valuation*, *risk*, *trend*, *portfolio* or *inflation* select specific agents. *report*, *comprehensive* or *full analysis* runs all of them plus the report writer. Anything unmatched falls back to `financial_statement`.
3. Each agent returns a validated `AgentResponse`. The orchestrator collects them and flags any disagreement between stances.
4. Confidence is a number from 0 to 1. Where the agent has a real signal it is computed from it (retrieval similarity for filings, sentiment scores for news). Otherwise it is a documented constant (see [limitations](#known-issues-and-limitations)).

---

## What is and isn't built

**Built and wired end to end**

- Ingestion → data engineering → classical ML → RAG → agents → explainability → API → dashboard → evaluation → CI/monitoring.
- Specialist agents are **deterministic and source-backed**, with no LLM calls. This is a deliberate choice recorded in [`docs/DECISIONS.md`](docs/DECISIONS.md), so every output can be traced to a real input.

**Not built yet (roadmap items in `plan.md`)**

- Authentication and multi-user support.
- Double-entry accounting and the tax engine.
- CFA-grade portfolio analytics (holdings, weights and cost basis are not modelled; the portfolio agent reports `insufficient_data`).
- LLM-generated analysis. `.env.template` lists OpenRouter, Ollama and Plaid settings, but the code does not use them yet.
- ChromaDB and Redis. They appear in the architecture and compose files but are not used by the application code.
- Real alert evaluation (the Alerts page is UI only).

---

## Tech stack

- **Backend:** Python 3.11, FastAPI, Pydantic, psycopg 3, scikit-learn, joblib, httpx, prometheus-client
- **Data store:** PostgreSQL 15 with pgvector
- **Frontend:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS
- **Infra:** Docker Compose, GitHub Actions, Prometheus, Grafana

---

## Repository layout

```
.
├── plan.md                  # Full product roadmap (much larger than what is built)
├── docs/                    # PRD, ARCHITECTURE, DECISIONS, PROGRESS, EVAL_RESULTS, RAG_RESULTS
├── backend/
│   ├── main.py              # FastAPI app, endpoints, Prometheus middleware
│   ├── agents/              # system.py (agents + router + orchestrator), schemas.py, tests/
│   ├── rag/                 # HTML → chunks → hashing embeddings → pgvector → cited_answer()
│   ├── ingestion/           # connectors/ (6 sources), validation, scheduler, live cache
│   ├── data_engineering/    # cleaning, features, dataset versioning
│   ├── ml/                  # benchmark.py + chronological split utility
│   ├── backtesting/         # engine.py (SMA, EMA, RSI, MACD signals + metrics)
│   ├── evaluation/          # hallucination, retrieval precision, latency, token cost, agreement
│   ├── Dockerfile, entrypoint.sh, requirements.txt, pyproject.toml
├── frontend/app/            # Pages: dashboard, company, portfolio, news, watchlists, chat, alerts, backtesting
├── fixtures/                # Recorded API samples + 3 Apple 10-K filings (annual_reports/)
├── models/                  # Trained model artifacts (.joblib) + metrics.json per model
├── agents/samples.json      # Saved real agent output (all explainability fields)
├── data_versions/           # Content-hash manifests of the cleaned datasets
├── infra/                   # docker-compose.yml (dev), init-db.sql, prometheus, grafana
├── docker-compose.prod.yml  # Production-style stack (adds Prometheus + Grafana)
└── .github/workflows/ci.yml
```

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 22 (matches the Dockerfile and CI)
- Docker (easiest way to get PostgreSQL with pgvector)

> The commands below follow the repo's code and config. Check them against your environment on first run.

### 1. Configure

```bash
cp .env.template backend/.env
```

The app runs without API keys. Live endpoints fall back to bundled fixtures. Optional keys:

| Variable | Used for |
|---|---|
| `DATABASE_URL` | Postgres connection (default `postgresql://postgres:postgres@localhost:5432/ai_financial_advisor`) |
| `ALPHA_VANTAGE_API_KEY` | Live quote ingestion (falls back to `demo`) |
| `FINNHUB_API_KEY` | Required for a *complete* live ingestion run |
| `SEC_USER_AGENT` | Contact string required by SEC EDGAR |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins (default `http://localhost:3000,http://127.0.0.1:3000`) |

### 2. Run locally (recommended for development)

**Start PostgreSQL + pgvector**

```bash
docker run -d --name afa-postgres -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ai_financial_advisor \
  pgvector/pgvector:pg15
```

**Backend** (run from the repo root, because imports use the `backend.` package path)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

python -m backend.rag.pipeline                    # chunk + embed the 3 Apple 10-Ks into pgvector (512 chunks)
INGESTION_FIXTURES=1 python -m backend.ingestion.scheduler   # optional: load fixture records into Postgres

uvicorn backend.main:app --reload --port 8000     # API docs at http://localhost:8000/docs
```

The `financial_statement` agent queries Postgres, and it is also the default route for unmatched queries, so run the RAG step before using `/orchestrate`.

**Frontend**

```bash
cd frontend
npm ci
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev    # http://localhost:3000
```

### 3. Run with Docker Compose

```bash
cp .env.template backend/.env
docker compose -f infra/docker-compose.yml up --build
# Then load the filings into the running database:
docker compose -f infra/docker-compose.yml exec backend python -m backend.rag.pipeline
```

This starts Postgres (5432), Redis (6379), the backend (8000) and the frontend (3000). See [Known issues](#known-issues-and-limitations) for a browser/API-URL caveat in this mode.

### Useful commands

```bash
python -m backend.agents.run_samples        # regenerate agents/samples.json
python -m backend.ml.benchmark              # retrain the 5 models, rewrite models/*/metrics.json
python -m backend.rag.evaluate              # retrieval precision@1 against the database
python -m backend.evaluation.hallucination_rate   # likewise: latency, token_cost, retrieval_precision, agent_agreement, forecast_accuracy
```

The `backend.evaluation.*` scripts append their results to `docs/EVAL_RESULTS.md`.

---

## API reference

Base URL: `http://localhost:8000`. Interactive docs are at `/docs`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check, returns `{"status": "ok"}` |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/v1/orchestrate` | `{"query": "..."}` → `{query, agents, results[], disagreements[]}` |
| GET | `/api/v1/agents` | Names of the available agents |
| GET | `/api/v1/market-data/{symbol}` | 3-month daily closes, last price and % change. Live from Yahoo (60 s cache), fixture fallback for the demo symbol |
| GET | `/api/v1/news?limit=10&symbol=` | Merged Google News RSS headlines (5 min cache), fixture fallback |
| GET | `/api/v1/macro/{series_id}` | Latest FRED observation (1 h cache), fixture fallback |
| POST | `/api/v1/backtest` | `{symbol, strategy, start_date, end_date}` → return, drawdown, Sharpe, trades, win rate, equity curve |

Every data endpoint returns a `live` flag so the UI can tell real data from fixtures.

```bash
curl -s -X POST localhost:8000/api/v1/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query":"Apple revenue 2025"}' | python -m json.tool
```

---

## Data and models

**Data sources:** Yahoo Finance, Alpha Vantage, Finnhub (credential-gated), SEC EDGAR, FRED, Google News RSS. Recorded samples live in `fixtures/` so tests and demos are deterministic.

**Embeddings:** deterministic 256-dimension `HashingVectorizer` vectors. This needs no external embedding API and gives reproducible retrieval, but retrieval is lexical rather than semantic.

**Models in `models/`:** each folder contains `model.joblib` and `metrics.json` (baseline, target, sample count, ship decision).

| Model | Task | Ship decision recorded in the repo |
|---|---|---|
| `forecasting` | Next-value price forecast | **Hold:** 5 observations |
| `sentiment` | Headline sentiment | **Hold:** weak keyword labels on 20 RSS titles |
| `anomaly_detection` | Return anomalies | **Hold:** 4 observations |
| `company_similarity` | Entity-overlap similarity | **Hold:** not a validated benchmark |
| `risk_prediction` | Risk classification | **Hold:** 3 test labels |

All five are intentionally marked *hold*. The fixture corpus is too small to support real models, so these show a leakage-safe pipeline rather than predictive power. The sentiment model is the only one the agents actually load.

---

## Evaluation results

Recorded by the repo's own scripts in [`docs/EVAL_RESULTS.md`](docs/EVAL_RESULTS.md) and [`docs/RAG_RESULTS.md`](docs/RAG_RESULTS.md). These numbers were copied from the repo's own recorded runs and were not re-run when this README was written.

| Metric | Result | Notes |
|---|---|---|
| Retrieval precision@1 | 4/5 (0.80) | 5 queries over 512 chunks |
| Retrieval precision@3 | 100% | 5 queries, expected filing found in top 3 |
| Citation hallucination rate | 5.77% | 20 samples; share of evidence items failing a citation-validity check |
| Orchestration latency | mean 30.8 ms, median 15.7 ms | 10 runs, local, fixture-backed |
| Estimated token cost | ~1,550 tokens, ~$0.0009/query | Estimated at gpt-4o-mini prices; the system does not call an LLM today |
| Agent agreement | 71.4% | 5 of 7 stance-bearing queries agreed |
| Forecast accuracy | not evaluable | Fixture too small |

---

## Testing and CI

```bash
pytest backend -m "not slow" -v     # skips live external-API smoke tests
```

- Tests cover every agent, the explainability schema, citation behaviour, the RAG pipeline, the chronological splits, ingestion connectors and the backtest engine. Several need a running Postgres.
- `-m slow` runs live API smoke tests (needs network and keys).
- `.github/workflows/ci.yml` runs backend tests against Postgres and Redis service containers, builds the frontend, builds and pushes Docker images to GHCR on `main`, and can trigger Render and Vercel deploys if the secrets are set.

---

## Monitoring

Metrics exposed at `/metrics`: `http_requests_total`, `http_request_duration_seconds`, `orchestration_total`, `orchestration_duration_seconds`, `agent_confidence{agent}` and `active_connections`. `infra/grafana-dashboard.json` provides a 6-panel dashboard (request rate, latency, orchestration rate and latency, agent confidence, connections). With `docker-compose.prod.yml`, Prometheus is on `:9090` and Grafana on `:3003` (login `admin` and `GRAFANA_PASSWORD`, default `admin`, so change it).

---

## Known issues and limitations

Found by reading the code and config. They were not reproduced by running it.

**Product behaviour**
- **Agents lean on fixtures.** The valuation, technical, portfolio and macro agents read single recorded samples (one Alpha Vantage quote, 5 Yahoo bars, one FRED observation). Only the `/market-data`, `/news` and `/macro` endpoints fetch live data.
- **Some confidences are constants.** Valuation is 0.7, technical 0.6, portfolio 0.5, macro 0.8 and risk 0.4. Only `financial_statement` (retrieval similarity) and `news_intelligence` (sentiment) are computed from signals. `docs/DECISIONS.md` describes all of them as computed.
- **The valuation agent doesn't value anything.** It reports a market quote, not a DCF or comparables estimate.
- **Retrieval is lexical.** Hashing embeddings match shared words, not meaning.
- **Not financial advice.** This is a research prototype. The risk and portfolio agents say plainly that their data is insufficient.

**Engineering**
- **Docker + browser URL:** the compose files set `NEXT_PUBLIC_API_URL=http://backend:8000`. That value is baked into client-side code, and a browser on your machine cannot resolve the `backend` hostname. For local use, run the frontend with `npm run dev` as shown above.
- **`docker-compose.prod.yml`** uses `./backend` and `./frontend` as build contexts, but `backend/Dockerfile` copies paths relative to the repo root (`backend/…`, `fixtures/`, `models/`). The dev compose in `infra/` uses the repo root as context and is the safer path. The CI Docker job appears to have the same context mismatch.
- **Prometheus target port:** `infra/prometheus.yml` scrapes `backend:8001`, while the backend listens on 8000.
- **`backend/pyproject.toml`** declares `readme = "README.md"`, but there is no `backend/README.md`, which can break `pip install -e ./backend`.
- **Next.js 14.2.24** is pinned and `docs/DECISIONS.md` notes open security advisories. Upgrade before any public deployment.
- Dependencies in `backend/requirements.txt` are pinned. `CORS` defaults to localhost only. There is no authentication.

---

## Documentation map

| File | What's inside |
|---|---|
| [`plan.md`](plan.md) | The full 12-week product plan and success criteria |
| [`docs/PRD.md`](docs/PRD.md) | Objectives, scope and success metrics |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System shape and per-phase storage and design notes |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Decision log with the reasoning behind each choice |
| [`docs/PROGRESS.md`](docs/PROGRESS.md) | Phase-by-phase completion checklist |
| [`docs/EVAL_RESULTS.md`](docs/EVAL_RESULTS.md), [`docs/RAG_RESULTS.md`](docs/RAG_RESULTS.md) | Recorded evaluation runs |

## Data attribution

Market and filing data come from public sources (SEC EDGAR, FRED, Yahoo Finance, Alpha Vantage, Finnhub, Google News RSS). Check each provider's terms before redistributing data or using it commercially.

# AI Financial Advisor SaaS - Complete Implementation Plan

## Project Overview

**Vision**: Build a production-grade AI-powered financial operating system combining Chartered Accountant (CA), CFA (Chartered Financial Analyst), Personal CFO, and Wealth Manager capabilities for local deployment.

**Architecture**: Multi-agent system using LangChain/LangGraph with RAG, double-entry accounting engine, CFA-standard portfolio analytics, and proactive CFO intelligence.

**Tech Stack**:
- **Backend**: FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis + ChromaDB
- **AI/ML**: LangChain 0.2 + LangGraph + OpenRouter (Nemotron) + Local Ollama
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui
- **Infrastructure**: Docker Compose + GitHub Actions CI/CD
- **Financial**: Alpha Vantage, yfinance, QuantLib, pandas-ta

---

## Phase 0: Infrastructure & Environment Setup (Week 1)

### 0.1 Docker Compose Production Stack
```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: ai_financial_advisor
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports: ["5432:5432"]
    volumes: ["postgres_data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: ["redis_data:/data"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  chromadb:
    image: chromadb/chroma:latest
    ports: ["8001:8000"]
    volumes: ["chroma_data:/chroma"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      chromadb:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  # Production additions
  nginx:
    image: nginx:alpine
    ports: ["443:443", "80:80"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/certs:/etc/nginx/certs
    depends_on: [backend, frontend]

  prometheus:
    image: prom/prometheus
    ports: ["9090:9090"]
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports: ["3001:3000"]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  chroma_data:
  grafana_data:
```

### 0.2 Environment Configuration (.env.template)
```bash
# Application
PROJECT_NAME="AI Financial Advisor SaaS"
VERSION="1.0.0"
API_V1_STR="/api/v1"
ENVIRONMENT="development"

# Security
SECRET_KEY="generate-with-openssl-rand-base64-32"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM="HS256"

# Database
DATABASE_URL="postgresql://postgres:postgres@postgres:5432/ai_financial_advisor"
POSTGRES_SERVER="postgres"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_DB="ai_financial_advisor"
POSTGRES_PORT="5432"

# Redis
REDIS_URL="redis://redis:6379/0"

# ChromaDB
CHROMADB_URL="http://chromadb:8000"

# LLM APIs
NEMOTRON_API_KEY=""
OPENROUTER_API_KEY=""
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
OLLAMA_BASE_URL="http://host.docker.internal:11434"
DEFAULT_LLM_MODEL="nvidia/nemotron-3-ultra"
EMBEDDING_MODEL="text-embedding-ada-002"

# Financial APIs
ALPHA_VANTAGE_API_KEY=""
PLAID_CLIENT_ID=""
PLAID_SECRET=""
PLAID_ENV="sandbox"

# Feature Flags
ENABLE_OCR=true
ENABLE_AI_INVESTMENT_RESEARCH=true
ENABLE_TAX_OPTIMIZATION=true
ENABLE_PORTFOLIO_OPTIMIZATION=true
ENABLE_CASHFLOW_FORECASTING=true
ENABLE_GOAL_PLANNING=true

# CA/CFA Settings
CA_TAX_COUNTRY="IN"
CFA_BENCHMARK_SYMBOL="NIFTY50"
```

### 0.3 SSL Certificates (mkcert)
```bash
# Install mkcert
brew install mkcert nss  # macOS
# or: choco install mkcert  # Windows

# Generate certificates
mkcert -install
mkcert -cert-file nginx/certs/localhost.pem -key-file nginx/certs/localhost-key.pem localhost 127.0.0.1 ::1
```

### 0.4 GitHub Actions CI/CD
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        ports: ["5432:5432"]
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install ruff mypy pytest pytest-asyncio pytest-cov

      - name: Run Ruff
        run: cd backend && ruff check .

      - name: Run MyPy
        run: cd backend && mypy app/

      - name: Run Tests
        run: cd backend && pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build-and-deploy:
    needs: lint-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker images
        run: docker-compose build

      - name: Run integration tests
        run: |
          docker-compose up -d
          sleep 30
          docker-compose exec -T backend pytest tests/integration/
          docker-compose down
```

### 0.5 Deliverables Checklist
- [ ] `docker-compose up` starts all services
- [ ] Backend at `https://localhost:8000/docs`
- [ ] Frontend at `https://localhost:3000`
- [ ] PostgreSQL with pgvector extension
- [ ] Redis for caching/Celery
- [ ] ChromaDB for vector storage
- [ ] Nginx SSL termination
- [ ] Prometheus + Grafana monitoring
- [ ] CI/CD pipeline passing

---

## Phase 1: Core Backend - Auth, Database, API (Week 2)

### 1.1 Database Models (Complete + Extensions)
```
backend/app/db/models.py
```

**Existing Models** (extend with new fields):
- User - add: `mfa_secret`, `mfa_enabled`, `oauth_provider`, `oauth_id`, `role` (Admin/User/Auditor/CA/CFA)
- Account, Transaction, Investment, Budget, Goal, TaxRecord

**New Models Required**:
```python
# Double-entry accounting
class JournalEntry(Base):
    id, date, description, reference, status, source, created_by_id
    lines: relationship(JournalLine)

class JournalLine(Base):
    id, entry_id, account_id, debit, credit, description, currency, fx_rate

class ChartOfAccount(Base):
    id, code, name, type (asset/liability/equity/income/expense), parent_id, currency, is_active

# Tax engine
class TaxReturn(Base):
    id, user_id, tax_year, country, status, total_income, total_deductions, tax_liability, refund_due

class TaxForm(Base):
    id, return_id, form_type (ITR1/ITR2/1040), data_json, generated_at

# Portfolio analytics
class PortfolioSnapshot(Base):
    id, portfolio_id, date, total_value, cash_value, daily_return, benchmark_return

class PerformanceMetric(Base):
    id, portfolio_id, date, metric_name, value, period (daily/monthly/yearly)

# Market data
class SecurityMaster(Base):
    id, symbol, name, exchange, currency, asset_class, sector, industry, is_active

class MarketData(Base):
    id, security_id, date, open, high, low, close, volume, adjusted_close, dividend, split
```

### 1.2 Alembic Migrations
```bash
cd backend
alembic init alembic
# Configure alembic/env.py for async
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

### 1.3 Authentication System Enhancement
```
backend/app/core/security.py     # JWT, password hashing, MFA
backend/app/api/v1/endpoints/auth.py
```

**Features**:
- JWT access/refresh tokens (RS256 in production)
- TOTP MFA (pyotp + qrcode)
- OAuth2: Google, GitHub (authlib)
- Password reset (email token + frontend link)
- Role-based access: Admin, User, Auditor, CA, CFA
- API key management for integrations

### 1.4 API Endpoints Structure
```
backend/app/api/v1/
├── router.py
└── endpoints/
    ├── auth.py           # login, register, refresh, me, mfa, oauth, password-reset
    ├── users.py          # CRUD, profile, preferences
    ├── accounts.py       # CRUD, balance sync, reconciliation
    ├── transactions.py   # CRUD, filters, categorization, bulk import
    ├── budgets.py        # CRUD, alerts, rollover
    ├── investments.py    # CRUD, corporate actions, dividends
    ├── goals.py          # CRUD, progress tracking, projections
    ├── taxes.py          # Tax records, returns, forms, optimization
    ├── journals.py       # Double-entry CRUD, validation, posting
    ├── reports.py        # Financial statements, ratios, exports
    ├── portfolio.py      # Holdings, performance, analytics
    ├── optimization.py   # Efficient frontier, rebalancing
    ├── market_data.py    # Quotes, history, search
    ├── ai_assistant.py   # Chat, recommendations, explanations
    └── webhooks.py       # Plaid, email, notifications
```

### 1.5 Security Hardening
- **Audit Logging**: Every financial operation logged with user, timestamp, before/after state
- **PII Encryption**: Fernet encryption for SSN, PAN, bank account numbers at rest
- **Rate Limiting**: Per-user, per-endpoint with burst allowance
- **CORS/CSRF**: Strict origins, SameSite cookies
- **Input Validation**: Pydantic v2 with custom validators for financial data

### 1.6 Deliverables Checklist
- [ ] All auth flows working (login, register, MFA, OAuth, password reset)
- [ ] RBAC enforced on all endpoints
- [ ] Alembic migrations for all models
- [ ] Swagger docs at `/api/v1/docs`
- [ ] 90%+ test coverage for auth module
- [ ] Audit logging middleware
- [ ] API key CRUD endpoints

---

## Phase 2: Financial Data Layer (Week 3)

### 2.1 Bank Integration Service
```
backend/app/services/bank_integration/
├── __init__.py
├── base.py                 # AbstractBankClient interface
├── plaid_client.py         # Plaid sandbox/production
├── teller_client.py        # Alternative provider
├── yodlee_client.py        # Alternative provider
├── sync_service.py         # Celery tasks for background sync
└── models.py               # RawTransaction, SyncLog, Institution
```

**Plaid Integration**:
```python
# Sync flow: link_token -> public_token -> access_token -> transactions
# Webhook handling for: TRANSACTIONS_UPDATE, ITEM_LOGIN_REQUIRED, ERROR
# Cursor-based pagination for incremental sync
```

### 2.2 Document Intelligence Pipeline
```
backend/app/services/document_intelligence/
├── __init__.py
├── csv_parser.py           # Auto-detect columns, map to schema
├── pdf_parser.py           # pdfplumber + pytesseract OCR
├── excel_parser.py         # openpyxl with header detection
├── email_parser.py         # IMAP fetch, attachment extraction
├── categorizer.py          # ML categorization (see below)
├── validator.py            # Data quality checks
└── models.py               # UploadBatch, ParsedTransaction, CategorizationRule
```

### 2.3 ML Transaction Categorization
```
backend/app/services/document_intelligence/categorizer.py
```

**Architecture**:
1. **Rule Engine** (Priority 1): Merchant mapping, keyword rules, user-defined rules
2. **ML Model** (Priority 2): Transformer-based (DistilBERT fine-tuned on financial transactions)
3. **Embeddings** (Priority 3): Merchant name → embedding → nearest neighbor classification
4. **Confidence Scoring**: Rule=0.95, ML=0.85, Embedding=0.70
5. **Feedback Loop**: User corrections → retraining queue → weekly model update

**Models**:
```python
class CategorizationRule(Base):
    id, user_id, pattern, category, priority, is_active, match_count

class MerchantEmbedding(Base):
    id, merchant_name, embedding (vector), category, confidence

class CategorizationFeedback(Base):
    id, transaction_id, predicted_category, actual_category, user_id, created_at
```

### 2.4 Data Models (Staging)
```python
class RawTransaction(Base):
    id, upload_batch_id, source (plaid/csv/pdf/email), raw_data_json, 
    parsed_amount, parsed_date, parsed_description, parsed_merchant,
    status (pending/reviewed/accepted/rejected), categorized_category, confidence

class UploadBatch(Base):
    id, user_id, source, filename, status, total_rows, processed_rows, error_rows, created_at
```

### 2.5 Deliverables Checklist
- [ ] Plaid sandbox: link → sync → transactions stored
- [ ] CSV/PDF/Excel upload → parsed transactions
- [ ] Email IMAP fetch for statements
- [ ] Categorization >90% accuracy on test data
- [ ] Background sync via Celery (every 6 hours)
- [ ] Webhook handling for real-time updates
- [ ] Duplicate detection and merging

---

## Phase 3: CA Accounting Engine (Week 4-5) - CRITICAL PATH

### 3.1 Double-Entry Core
```
backend/app/engines/accounting/
├── __init__.py
├── journal.py              # JournalEntry, JournalLine, validation
├── ledger.py               # GeneralLedger, TrialBalance, AccountBalance
├── chart_of_accounts.py    # Hierarchy, default templates (IN/US/UK)
├── posting.py              # Post to ledger, validate balance
├── period_close.py         # Month-end, year-end, closing entries
├── reconciliation.py       # Bank reconciliation, matching engine
└── models.py               # Extended models
```

**Journal Entry Validation**:
```python
def validate_journal_entry(entry: JournalEntry) -> ValidationResult:
    # 1. At least 2 lines
    # 2. Sum(debits) == Sum(credits) per currency
    # 3. All accounts exist and active
    # 4. No self-referencing lines
    # 5. Date within open period
    # 6. Reference format compliance
```

**Default Chart of Accounts (India)**:
```
1000 - Assets
  1100 - Current Assets
    1110 - Cash & Bank
    1120 - Accounts Receivable
    1130 - Inventory
    1140 - Prepaid Expenses
  1200 - Fixed Assets
    1210 - Property, Plant & Equipment
    1220 - Intangible Assets
    1230 - Accumulated Depreciation
2000 - Liabilities
  2100 - Current Liabilities
    2110 - Accounts Payable
    2120 - GST Payable
    2130 - TDS Payable
    2140 - Short-term Loans
  2200 - Non-Current Liabilities
3000 - Equity
  3100 - Share Capital
  3200 - Reserves & Surplus
4000 - Income
  4100 - Revenue from Operations
  4200 - Other Income
5000 - Expenses
  5100 - Cost of Goods Sold
  5200 - Employee Benefits
  5300 - Finance Costs
  5400 - Depreciation & Amortization
  5500 - Other Expenses
```

### 3.2 Automated Journal Generation
```
backend/app/engines/accounting/auto_journal.py
```

**Transaction → Journal Mapping**:
```python
MAPPING_RULES = {
    "salary_credit": {
        "debit": "1110",  # Cash & Bank
        "credit": "4110", # Salary Income
    },
    "rent_expense": {
        "debit": "5510",  # Rent Expense
        "credit": "1110", # Cash & Bank
    },
    "gst_payment": {
        "debit": "2120",  # GST Payable
        "credit": "1110", # Cash & Bank
    },
    # ... 50+ rules for common patterns
}
```

**Features**:
- Recurring entries (depreciation, amortization, rent, subscriptions)
- Bank reconciliation automation (match by amount/date/reference)
- Inter-company eliminations (future multi-entity)
- Reversing entries for accruals

### 3.3 Financial Statements Engine
```
backend/app/engines/accounting/financial_statements/
├── __init__.py
├── balance_sheet.py        # Classified BS with notes
├── income_statement.py     # Multi-step P&L
├── cash_flow.py            # Direct + Indirect method
├── statement_changes_equity.py
├── notes_to_accounts.py    # Auto-generated notes
├── ratio_analysis.py       # Liquidity, Solvency, Profitability, Efficiency
└── formatter.py            # PDF, Excel, JSON, XBRL export
```

**Standards Compliance**:
- **Ind AS** (India) - Primary
- **GAAP** (US) - Secondary
- **IFRS** - Tertiary
- Configurable per user/entity

### 3.4 Tax Engine (CA Core)
```
backend/app/engines/tax/
├── __init__.py
├── income_tax.py           # Slab calculation, deductions (80C, 80D, 80CCD, etc.)
├── capital_gains.py        # STCG/LTCG, indexation, grandfathering, crypto
├── gst_vat.py              # GSTR-1, GSTR-3B, ITC reconciliation, e-invoicing
├── tds.py                  # TDS deduction, Form 16/16A, certificates
├── tax_optimizer.py        # Regime comparison, investment planning, loss carryforward
├── tax_forms.py            # ITR-1, ITR-2, ITR-3, ITR-4 generation (XML/JSON)
├── advance_tax.py          # Quarterly installment calculation
└── country_rules/
    ├── india.py
    ├── us.py
    └── uk.py
```

**India Tax Features (FY 2024-25)**:
- Old vs New regime comparison
- Section 80C (1.5L), 80D (25K/50K), 80CCD(1B) (50K), 80E, 80G, 80TTA
- Capital gains: STCG 15%, LTCG 10% >1L (equity), 20% with indexation (debt/property)
- Crypto: 30% flat + 1% TDS
- GST: Composition vs Regular, ITC rules, RCM
- TDS: All sections, certificate generation (Form 16/16A/26Q/27Q)

### 3.5 Compliance & Audit
- **Audit Trail**: Immutable log of every journal entry, approval, modification
- **Document Attachment**: Link invoices, receipts, contracts to journal lines
- **Approval Workflow**: Maker-Checker for entries > threshold
- **Export**: CSV (auditor), Excel (management), PDF (board), XBRL (regulatory)
- **Lock Periods**: Prevent edits to closed periods

### 3.6 Deliverables Checklist
- [ ] Double-entry system always balances
- [ ] Auto-generate journals from 90% of transaction types
- [ ] Generate all 4 financial statements + notes
- [ ] Tax calculator matches government portal (income tax, GST, TDS)
- [ ] Tax optimizer suggests optimal regime/investments
- [ ] Audit-ready export with full traceability
- [ ] Period close automation (monthly/yearly)
- [ ] Bank reconciliation >95% auto-match rate

---

## Phase 4: CFA Investment Engine (Week 6-7)

### 4.1 Portfolio Management
```
backend/app/engines/portfolio/
├── __init__.py
├── portfolio.py            # Portfolio, Position, Holding models
├── holdings.py             # Real-time holdings with P&L
├── transactions.py         # Buy/Sell/Dividend/Split/Merger
├── corporate_actions.py    # Automated CA processing
├── cash_management.py      # Dividends, interest, withdrawals
└── rebalancing.py          # Drift detection, order generation
```

**Models**:
```python
class Portfolio(Base):
    id, user_id, name, base_currency, benchmark, strategy, risk_profile, created_at

class Position(Base):
    id, portfolio_id, security_id, quantity, avg_cost, current_price, 
    market_value, unrealized_pnl, realized_pnl, weight, updated_at

class PortfolioTransaction(Base):
    id, portfolio_id, security_id, type (buy/sell/dividend/split/merger/spin_off),
    quantity, price, amount, fees, tax, currency, fx_rate, trade_date, settle_date, status
```

### 4.2 Performance Analytics (GIPS Compliant)
```
backend/app/engines/analytics/
├── __init__.py
├── returns.py              # TWR, MWR/IRR, Modified Dietz
├── risk.py                 # VaR (Parametric/Historical/Monte Carlo), CVaR, Beta, Sharpe, Sortino, Calmar, Information Ratio, Treynor, Jensen Alpha
├── attribution.py          # Brinson-Hood-Beebower (Allocation/Selection/Interaction), Factor attribution
├── benchmarking.py         # Custom benchmarks, peer comparison
├── drawdown.py             # Max DD, Ulcer Index, Recovery analysis
├── ratios.py               # Up/Down Capture, Omega, Kappa, Calmar
└── reporting.py            # GIPS-compliant reports, tear sheets
```

**Key Formulas**:
```python
# Time-Weighted Return (Daily Valuation)
def twr(portfolio_values: List[Tuple[date, float]], cash_flows: List[CashFlow]) -> float:
    sub_periods = split_by_cash_flows(portfolio_values, cash_flows)
    return np.prod([1 + (end - start - cf) / start for start, end, cf in sub_periods]) - 1

# Money-Weighted Return (IRR)
def mwr(cash_flows: List[Tuple[date, float]]) -> float:
    return numpy_financial.irr(cash_flows)

# VaR (Historical, 95%, 1-day)
def var_historical(returns: np.array, confidence=0.95) -> float:
    return np.percentile(returns, (1 - confidence) * 100)

# Brinson Attribution
def brinson_attribution(portfolio_weights, benchmark_weights, portfolio_returns, benchmark_returns):
    allocation = sum((pw - bw) * br for pw, bw, br in zip(portfolio_weights, benchmark_weights, benchmark_returns))
    selection = sum(bw * (pr - br) for bw, pr, br in zip(benchmark_weights, portfolio_returns, benchmark_returns))
    interaction = sum((pw - bw) * (pr - br) for pw, bw, pr, br in zip(portfolio_weights, benchmark_weights, portfolio_returns, benchmark_returns))
    return allocation, selection, interaction
```

### 4.3 Market Data Service
```
backend/app/services/market_data/
├── __init__.py
├── alpha_vantage.py        # Equities, FX, Crypto, Fundamentals
├── yahoo_finance.py        # yfinance wrapper with caching
├── polygon_io.py           # Alternative (options, tick data)
├── fred.py                 # Macro: GDP, CPI, Fed rates, Treasury yields
├── sec_filings.py          # EDGAR 10-K, 10-Q, 8-K parsing
├── nse_bse.py              # India-specific: NSE/BSE quotes, indices
├── price_cache.py          # Redis caching layer (TTL: 1min quote, 1hr daily)
└── models.py               # Quote, OHLCV, Fundamental, CorporateAction
```

### 4.4 Portfolio Optimization
```
backend/app/engines/optimization/
├── __init__.py
├── mean_variance.py        # Markowitz Efficient Frontier, CVXPY
├── black_litterman.py      # BL with views, confidence, equilibrium
├── risk_parity.py          # Equal Risk Contribution, Hierarchical RP
├── monte_carlo.py          # Simulation engine, path generation
├── constraints.py          # Linear (sector, position, turnover), Non-linear (VaR, ESG)
├── objective.py            # Max Sharpe, Min Variance, Max Return, Risk Budgeting
└── models.py               # OptimizationInput, OptimizationResult, EfficientFrontierPoint
```

**Optimization Features**:
- Long-only / Long-short constraints
- Position limits (max 10% per security, max 25% per sector)
- Turnover constraints (max 20% per rebalance)
- Transaction cost model (spread + commission + market impact)
- ESG constraints (min ESG score, exclude sectors)
- Factor constraints (beta neutrality, style tilts)
- Robust optimization (resampled efficient frontier)

### 4.5 Investment Research Engine
```
backend/app/engines/research/
├── __init__.py
├── fundamental.py          # DCF, Multiples (P/E, EV/EBITDA), Piotroski F-Score, Altman Z
├── technical.py            # 50+ indicators (RSI, MACD, Bollinger, Ichimoku, Wyckoff)
├── valuation.py            # DDM, FCFF/FCFE, Relative, Sum-of-Parts
├── credit_analysis.py      # Bond spreads, Duration, Convexity, Z-spread, OAS
├── esg.py                  # ESG scoring, Carbon footprint, SDG alignment
└── models.py               # ResearchReport, ValuationModel, TechnicalSignal
```

### 4.6 Deliverables Checklist
- [ ] Real-time portfolio with unrealized/realized P&L
- [ ] TWR/MWR matching custodian statements (<1bp difference)
- [ ] Risk dashboard: VaR, Greeks, Stress tests (2008, 2020, custom)
- [ ] Performance attribution (Allocation/Selection/Interaction)
- [ ] Efficient frontier visualization with constraints
- [ ] Rebalancing orders with tax-lot optimization
- [ ] Research reports for top 10 holdings
- [ ] Market data cached, <100ms quote latency

---

## Phase 5: AI Intelligence Layer (Week 8-9)

### 5.1 LLM Infrastructure
```
backend/app/ai/
├── __init__.py
├── llm_client.py           # OpenRouter + Ollama unified interface
├── embeddings.py           # OpenAI / Local (sentence-transformers)
├── vector_store.py         # ChromaDB wrapper with hybrid search
├── prompt_templates.py     # Financial domain prompts
├── guardrails.py           # Output validation, hallucination detection
├── cost_tracker.py         # Token usage, cost per request, budget alerts
└── models.py               # LLMRequest, LLMResponse, EmbeddingRequest
```

**LLM Client Design**:
```python
class LLMClient:
    def __init__(self):
        self.openrouter = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
        self.ollama = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    
    async def complete(self, request: LLMRequest) -> LLMResponse:
        # Route based on complexity: simple→Ollama, complex→OpenRouter
        # Fallback chain: Nemotron → GPT-4o → Claude-3.5 → Local
        # Streaming support for chat
        # Cost tracking per request
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        # Batch embeddings, cache in Redis
```

### 5.2 LangGraph Multi-Agent Framework
```
backend/app/ai/agents/
├── __init__.py
├── base_agent.py           # AbstractAgent with state, tools, memory
├── coordinator.py          # Supervisor router, task decomposition
├── accounting_agent.py     # CA specialist: journal, tax, compliance
├── investment_agent.py     # CFA specialist: portfolio, optimization, research
├── tax_agent.py            # Tax optimization, form filing, planning
├── risk_agent.py           # Risk assessment, stress testing, alerts
├── budget_agent.py         # Budget monitoring, variance analysis
├── planner_agent.py        # Goal planning, cashflow forecasting
└── models.py               # AgentState, ToolCall, AgentResponse
```

**LangGraph State Graph**:
```python
from langgraph.graph import StateGraph, END

# Define agent state
class AgentState(TypedDict):
    user_id: int
    messages: List[BaseMessage]
    current_agent: str
    task: str
    context: Dict
    tools_used: List[str]
    confidence: float
    requires_human: bool

# Coordinator routes to specialists
workflow = StateGraph(AgentState)
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("accounting", accounting_agent_node)
workflow.add_node("investment", investment_agent_node)
workflow.add_node("tax", tax_agent_node)
workflow.add_node("risk", risk_agent_node)
workflow.add_node("budget", budget_agent_node)
workflow.add_node("planner", planner_agent_node)

# Conditional routing based on intent classification
workflow.add_conditional_edges("coordinator", route_to_specialist)
workflow.add_edge("accounting", "coordinator")
workflow.add_edge("investment", "coordinator")
# ... all specialists return to coordinator
workflow.add_edge("coordinator", END)
```

### 5.3 RAG Knowledge Base
```
backend/app/ai/rag/
├── __init__.py
├── ingest.py               # Document ingestion pipeline
├── retriever.py            # Hybrid search (vector + keyword + graph)
├── knowledge_base.py       # Curated financial knowledge
└── sources/
    ├── accounting_standards/    # Ind AS, GAAP, IFRS PDFs
    ├── tax_codes/               # Income Tax Act, GST Act, Circulars
    ├── investment_theory/       # CFA curriculum, textbooks
    ├── regulations/             # SEBI, RBI, IRS, SEC filings
    └── user_documents/          # User's financial docs (private)
```

**Retrieval Strategy**:
1. **Hybrid Search**: BM25 (keyword) + Vector (semantic) + Graph (entity relationships)
2. **Re-ranking**: Cross-encoder reranker for top-20 → top-5
3. **Citation Tracking**: Every chunk has source, page, section metadata
4. **Access Control**: User docs isolated, public knowledge shared

### 5.4 Proactive CFO Engine
```
backend/app/engines/cfo/
├── __init__.py
├── monitor.py              # Continuous monitoring (Celery beat)
├── alerts.py               # Rule-based + ML anomaly detection
├── recommendations.py      # Ranked action items with evidence
├── scenarios.py            # What-if simulation (Monte Carlo)
├── digital_twin.py         # Financial simulation engine
└── models.py               # Alert, Recommendation, Scenario, SimulationResult
```

**Monitoring Triggers**:
```python
TRIGGERS = {
    "salary_credited": {
        "condition": "transaction.category == 'salary' and amount > 0",
        "actions": ["allocate_to_goals", "check_emergency_fund", "suggest_investment"]
    },
    "large_expense": {
        "condition": "transaction.amount > budget.category_limit * 0.5",
        "actions": ["budget_alert", "suggest_alternative", "check_cashflow"]
    },
    "portfolio_drift": {
        "condition": "portfolio.max_weight_deviation > 0.05",
        "actions": ["rebalance_recommendation", "tax_lot_analysis"]
    },
    "tax_deadline": {
        "condition": "days_until_deadline < 30",
        "actions": ["tax_optimization_review", "advance_tax_calculation"]
    },
    "emergency_fund_low": {
        "condition": "emergency_fund_months < 3",
        "actions": ["priority_alert", "liquidation_suggestions"]
    },
    "concentration_risk": {
        "condition": "portfolio.single_position_weight > 0.20",
        "actions": ["diversification_recommendation", "risk_metrics"]
    },
}
```

### 5.5 Explainable AI Framework
```
backend/app/ai/explainability/
├── __init__.py
├── explainer.py            # SHAP, LIME, Counterfactual explanations
├── citation_tracker.py     # Source attribution for every claim
├── confidence_calibrator.py # Temperature scaling, Platt scaling
├── feedback_collector.py   # User feedback → model improvement
└── models.py               # Explanation, Citation, ConfidenceScore
```

**Recommendation Card Structure**:
```python
@dataclass
class RecommendationCard:
    id: str
    title: str
    description: str
    why: str                    # Natural language reasoning
    evidence: List[Citation]    # Sources: regulation, historical data, model
    risk: str                   # What could go wrong
    alternative: str            # Next best option
    confidence: float           # 0-1 calibrated
    action_required: bool       # User must approve
    estimated_impact: Dict      # Financial projections
    expires_at: datetime        # Time sensitivity
```

### 5.6 Guardrails Implementation
```
backend/app/ai/guardrails.py
```

**Validation Layers**:
```python
class Guardrails:
    def __init__(self):
        self.financial_validator = FinancialValidator()
        self.regulatory_checker = RegulatoryChecker()
        self.hallucination_detector = HallucinationDetector()
        self.pii_filter = PIIFilter()
    
    def validate_output(self, response: str, context: Dict) -> ValidationResult:
        # 1. PII detection and redaction
        # 2. Financial fact-checking (rates, limits, formulas)
        # 3. Regulatory compliance (no unauthorized advice)
        # 4. Hallucination detection (self-consistency, retrieval verification)
        # 5. Confidence scoring
        # 6. Action authorization (requires human approval for trades, tax filing)
```

**Specific Rules**:
- No specific buy/sell recommendations without disclaimer
- Tax advice must cite section/act
- Portfolio changes require risk disclosure
- All calculations shown with formula
- Confidence < 0.7 → escalate to human

### 5.7 Deliverables Checklist
- [ ] Multi-agent chat with specialist routing (<3s response)
- [ ] RAG answers tax/accounting questions with citations
- [ ] Proactive daily/weekly financial briefing email
- [ ] What-if scenario simulator (Monte Carlo, 10k paths)
- [ ] Explainable recommendation cards with evidence
- [ ] Guardrails: 0 hallucinations on financial facts
- [ ] Cost tracking: <$0.01 per query average
- [ ] Feedback loop improving agent accuracy weekly

---

## Phase 6: Frontend - Next.js Dashboard (Week 10-11)

### 6.1 Migration: CRA → Next.js 14
```bash
cd frontend
npx create-next-app@14 . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
# Migrate components, pages, context, hooks
```

### 6.2 Project Structure
```
frontend/src/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── mfa/page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx              # Sidebar, header, navigation
│   │   ├── page.tsx                # Overview: net worth, cashflow, alerts
│   │   ├── accounts/page.tsx       # CA: Accounts, Ledger, Reconciliation
│   │   ├── transactions/page.tsx   # Categorization, rules, bulk edit
│   │   ├── budgets/page.tsx        # Budget vs Actual, variance
│   │   ├── taxes/page.tsx          # CA: Tax Center, Forms, Optimization
│   │   ├── investments/page.tsx    # CFA: Portfolio, Holdings, Transactions
│   │   ├── analytics/page.tsx      # CFA: Performance, Attribution, Risk
│   │   ├── optimization/page.tsx   # CFA: Efficient Frontier, Rebalancing
│   │   ├── goals/page.tsx          # Goal Planning, Projections
│   │   ├── cashflow/page.tsx       # Forecasting, Scenarios
│   │   ├── reports/page.tsx        # Financial Statements, Exports
│   │   └── ai-assistant/page.tsx   # Chat, Recommendations, Insights
│   ├── api/                        # Next.js API routes (proxy to backend)
│   └── globals.css
├── components/
│   ├── ui/                         # shadcn/ui components
│   ├── charts/                     # Recharts wrappers
│   ├── forms/                      # React Hook Form + Zod
│   ├── tables/                     # TanStack Table
│   └── financial/                  # Domain-specific components
├── lib/
│   ├── api.ts                      # Axios instance, React Query
│   ├── auth.ts                     # Auth utilities
│   ├── utils.ts                    # Formatters, validators
│   └── constants.ts
├── hooks/
│   ├── useAuth.ts
│   ├── useAccounts.ts
│   ├── usePortfolio.ts
│   └── useAIAssistant.ts
└── types/
    ├── api.ts
    ├── financial.ts
    └── ui.ts
```

### 6.3 CA-Specific Components
```
frontend/src/components/financial/ca/
├── JournalEntryForm.tsx          # Debit/Credit grid with validation
├── TrialBalanceView.tsx          # Drill-down to accounts
├── FinancialStatementBuilder.tsx # Drag-drop statement builder
├── TaxFormWizard.tsx             # ITR-1/2/3/4 step-by-step
├── GSTReturnDashboard.tsx        # GSTR-1/3B, ITC reconciliation
├── AuditTrailViewer.tsx          # Immutable log with filters
└── ComplianceCalendar.tsx        # Due dates, reminders
```

### 6.4 CFA-Specific Components
```
frontend/src/components/financial/cfa/
├── PortfolioHoldingsTable.tsx    # Real-time with P&L, weights
├── PerformanceAttributionChart.tsx # Brinson waterfall
├── RiskDashboard.tsx             # VaR, Greeks, Stress test results
├── EfficientFrontierViz.tsx      # Interactive frontier with constraints
├── ResearchReportViewer.tsx      # DCF, Comparables, Technical
├── RebalancingOrderTicket.tsx    # Tax-aware rebalancing
└── FactorExposureHeatmap.tsx     # Style, sector, country factors
```

### 6.5 Shared Components
```
frontend/src/components/financial/shared/
├── FinancialHealthScore.tsx      # Radial gauge 0-100
├── NetWorthWaterfall.tsx         # Sankey diagram
├── CashflowSankey.tsx            # Income → Expenses → Savings → Investments
├── GoalProgressTracker.tsx       # Timeline with projections
├── AlertNotificationCenter.tsx   # Real-time SSE/WebSocket
├── AIRecommendationCard.tsx      # Explainable card with actions
├── CurrencyFormatter.tsx         # Multi-currency, locale-aware
└── DateRangePicker.tsx           # Fiscal year, quarter, custom
```

### 6.6 Real-Time Features
- **WebSocket/SSE**: Portfolio updates, alerts, AI streaming
- **TanStack Query**: Server state with background refetch
- **Optimistic Updates**: Immediate UI feedback for mutations
- **Offline Support**: Service worker for critical reads

### 6.7 Deliverables Checklist
- [ ] Next.js 14 app at `https://localhost:3000`
- [ ] All 14 dashboard pages functional
- [ ] Real-time portfolio updates (<2s latency)
- [ ] Dark/Light mode with system preference
- [ ] Mobile responsive (tablet + phone)
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Internationalization (i18n) ready
- [ ] Storybook for component documentation

---

## Phase 7: Integration, Testing & Deploy (Week 12)

### 7.1 Integration Testing
```
tests/integration/
├── test_auth_flow.py
├── test_bank_sync.py
├── test_journal_generation.py
├── test_tax_calculation.py
├── test_portfolio_performance.py
├── test_optimization.py
├── test_ai_recommendations.py
├── test_e2e_scenarios.py
└── fixtures/
    ├── sample_transactions.csv
    ├── sample_portfolio.csv
    └── tax_scenarios.json
```

**Key E2E Scenarios**:
```python
# Scenario 1: Complete CA workflow
async def test_ca_workflow():
    # 1. User onboards → connects bank → transactions sync
    # 2. Transactions categorized → journals auto-generated
    # 3. Trial balance verified → financial statements generated
    # 4. Tax calculated → optimization suggested → ITR form generated
    # 5. Export audit package for CA review

# Scenario 2: Complete CFA workflow
async def test_cfa_workflow():
    # 1. User adds investments → market data enriches
    # 2. Portfolio performance calculated (TWR/MWR)
    # 3. Risk metrics computed (VaR, Greeks)
    # 4. Optimization runs → rebalancing orders
    # 5. Research reports generated for holdings

# Scenario 3: AI proactive workflow
async def test_ai_proactive():
    # 1. Salary credited → AI detects
    # 2. Allocation recommendation created
    # 3. User approves → journals posted
    # 4. Portfolio rebalanced → tax lots optimized
```

### 7.2 Load & Security Testing
```bash
# Locust load test
locust -f tests/load/locustfile.py --host=https://localhost:8000

# OWASP ZAP security scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://localhost:8000

# Penetration testing checklist
# - SQL injection, XSS, CSRF, SSRF, IDOR
# - Auth, path traversal
# - Rate limiting bypass, JWT vulnerabilities
# - File upload validation, XXE
```

### 7.3 CA/CFA Compliance Documentation
```
docs/compliance/
├── ca_methodology.md           # Accounting policies, revenue recognition
├── cfa_gips_compliance.md      # Performance calculation methodology
├── data_lineage.md             # Audit trail design, immutable logs
├── model_validation.md         # ML model docs, backtesting results
├── security_controls.md        # SOC2 mapping, encryption, access control
├── regulatory_mapping.md       # Ind AS, GAAP, SEC, SEBI, RBI
├── privacy_impact.md           # GDPR, DPDP Act compliance
└── disaster_recovery.md        # RPO/RTO, backup strategy
```

### 7.4 Production Docker Compose
```yaml
# docker-compose.prod.yml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Add: Loki for logs, Promtail for collection
  # Add: Backup service (pg_dump to S3)
  # Add: SSL auto-renewal (certbot)
```

### 7.5 Demo Data & Scenarios
```
scripts/seed_demo_data.py
```

**Demo User Profile**:
- 2 years of transactions (salary, expenses, investments)
- Diversified portfolio (equity, debt, gold, crypto)
- Tax scenarios: Salary + Capital Gains + Rental Income
- Goals: Emergency fund, House down payment, Retirement
- Budgets: Monthly categories with variance

### 7.6 Deliverables Checklist
- [ ] All integration tests passing (100%)
- [ ] Load test: 100 concurrent users, p95 < 500ms
- [ ] Security scan: 0 critical/high vulnerabilities
- [ ] Compliance docs ready for CA/CFA review
- [ ] One-command deploy: `docker-compose -f docker-compose.prod.yml up -d`
- [ ] Demo-ready with seeded data
- [ ] Backup/restore tested (RPO < 1hr, RTO < 4hr)
- [ ] Monitoring dashboards: API latency, error rates, DB connections, queue depth

---

## Phase 8: Advanced Features (Post-MVP)

### CA Advanced
- Multi-entity consolidation with elimination entries
- Fixed asset register with depreciation schedules (SLM, WDV, Units of Production)
- Payroll engine with statutory compliance (PF, ESI, PT, LWF)
- Audit automation: Sampling, Substantive testing, Analytics
- Transfer pricing documentation (Master File, Local File, CbCR)

### CFA Advanced
- Options analytics: Greeks, Volatility surface, Strategy builder (Iron Condor, Butterfly)
- Fixed income: Duration, Convexity, Key Rate Duration, OAS, Z-spread
- Alternative investments: PE (TVPI, DPI, IRR), Real Estate (Cap rate, DCF), Hedge Funds
- ESG integration: Carbon accounting, SFDR, TCFD reporting
- Factor investing: Fama-French 5-factor, PCA, Risk premia harvesting

### AI Advanced
- Voice financial assistant (Whisper + TTS)
- Autonomous rebalancing with human-in-loop approval
- Tax-loss harvesting automation (wash sale detection)
- Multi-currency support with FX hedging
- Family office: Multi-user, role-based, consolidated reporting

---

## Resource Requirements

### Team (Minimum Viable)
| Role | Phase 0-2 | Phase 3-4 | Phase 5-6 | Phase 7 |
|------|-----------|-----------|-----------|---------|
| Backend Engineer | 2 | 2 | 2 | 1 |
| Frontend Engineer | 1 | 1 | 2 | 1 |
| DevOps/Infra | 1 | 0.5 | 0.5 | 1 |
| CA Domain Expert | 0.5 | 1 | 0.5 | 1 |
| CFA Domain Expert | 0.5 | 0.5 | 1 | 1 |
| ML Engineer | 0 | 0.5 | 1 | 0.5 |
| QA Engineer | 0.5 | 0.5 | 1 | 1 |

### Infrastructure (Local Development)
- **Hardware**: 32GB RAM, 8+ CPU cores, 500GB NVMe SSD
- **Software**: Docker Desktop / Rancher Desktop, mkcert, ngrok/Cloudflare Tunnel
- **External**: OpenRouter API, Alpha Vantage, Plaid Sandbox, Ollama (local LLM)

---

## Timeline Summary

| Phase | Duration | Focus | Key Deliverable |
|-------|----------|-------|-----------------|
| 0 | 1 week | Infra | Docker, CI/CD, SSL, Monitoring |
| 1 | 1 week | Core Backend | Auth, RBAC, API, Migrations |
| 2 | 1 week | Data Layer | Bank sync, Upload, Categorization |
| 3 | 2 weeks | CA Engine | Double-entry, Tax, Statements |
| 4 | 2 weeks | CFA Engine | Portfolio, Analytics, Optimization |
| 5 | 2 weeks | AI Layer | Agents, RAG, CFO, Guardrails |
| 6 | 2 weeks | Frontend | Next.js Dashboard, Real-time |
| 7 | 1 week | Integration | Tests, Security, Compliance, Deploy |
| **Total** | **12 weeks** | | **Production-ready MVP** |

---

## Success Criteria

### Technical KPIs
- [ ] API p95 latency < 500ms
- [ ] AI recommendation latency < 5s
- [ ] Portfolio update latency < 2s
- [ ] Test coverage > 85% (unit + integration)
- [ ] Zero critical/high security vulnerabilities
- [ ] Docker image size < 2GB (backend), < 1GB (frontend)

### CA/CFA Functional KPIs
- [ ] Trial balance always balances (sum = 0)
- [ ] Tax calculation matches government portal (100%)
- [ ] Performance matches custodian statements (<1bp)
- [ ] Optimization improves Sharpe ratio >10%
- [ ] Categorization accuracy >95% on user data
- [ ] GIPS-compliant performance reports

### User Experience
- [ ] Onboarding < 5 minutes (bank connect → first insight)
- [ ] Daily active use > 10 minutes
- [ ] NPS > 50
- [ ] Support tickets < 5% users/month
- [ ] Mobile usability score > 90

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Plaid API changes | Medium | High | Abstract bank adapter, multiple providers (Teller, Yodlee) |
| LLM hallucination | High | High | Guardrails, RAG, human-in-loop for actions, confidence thresholds |
| Tax law changes | Medium | High | Configurable rule engine, annual update process, versioned tax rules |
| Performance at scale | Low | Medium | Load test early, aggressive caching, read replicas, pagination |
| Regulatory compliance | Medium | High | CA/CFA review at each phase, immutable audit trail, legal review |
| Data quality | High | Medium | Validation at ingestion, duplicate detection, reconciliation reports |
| Model drift | Medium | Medium | Feedback loop, monthly retraining, A/B testing, monitoring |

---

## Next Steps (Immediate)

1. **Week 1**: Execute Phase 0 completely
   - `docker-compose up` → all services healthy
   - GitHub Actions CI/CD passing
   - SSL certificates working
   - Monitoring dashboards visible

2. **Week 2**: Complete Phase 1
   - Alembic migrations for all models
   - MFA + OAuth2 + RBAC
   - All CRUD endpoints with validation
   - Audit logging + PII encryption

3. **Week 3**: Phase 2 Data Layer
   - Plaid sandbox integration
   - CSV/PDF parser with categorization
   - Background sync with Celery

4. **Weeks 4-5**: Phase 3 CA Engine (parallel with Phase 2)
   - Double-entry core with validation
   - Auto-journal from transactions
   - Financial statements + Tax engine

5. **Weeks 6-7**: Phase 4 CFA Engine
   - Portfolio management + Analytics
   - Market data integration
   - Optimization engine

6. **Weeks 8-9**: Phase 5 AI Layer
   - LangGraph multi-agent system
   - RAG knowledge base
   - Proactive CFO + Guardrails

7. **Weeks 10-11**: Phase 6 Frontend
   - Next.js 14 migration
   - All dashboard pages
   - CA/CFA specific components

8. **Week 12**: Phase 7 Integration & Deploy
   - E2E tests, load test, security scan
   - Compliance documentation
   - Production deploy + Demo data

---

## Appendix: Key Technical Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| FastAPI + SQLAlchemy 2.0 | Async, type-safe, performance | Django, Flask, NestJS |
| PostgreSQL + pgvector | ACID + vector search in one DB | Pinecone, Weaviate, Qdrant |
| LangGraph over LangChain agents | Stateful, cyclical, human-in-loop | AutoGen, CrewAI, Semantic Kernel |
| Next.js 14 App Router | RSC, streaming, SEO, performance | Remix, Vite+React, CRA |
| ChromaDB | Local-first, open-source, hybrid search | pgvector-only, Pinecone |
| Celery + Redis | Mature, scalable, monitoring | Dramatiq, RQ, Temporal |
| Tailwind + shadcn/ui | Customizable, accessible, fast dev | MUI, Chakra, Ant Design |
| OpenRouter + Ollama | Model flexibility, cost control, local fallback | Direct OpenAI, Anthropic only |

---

*Document Version: 1.0*  
*Last Updated: 2026-07-19*  
*For: Local Deployment with CA/CFA Integration*  
*Location: ~/Downloads/ai-financial-advisor-plan/plan.md*
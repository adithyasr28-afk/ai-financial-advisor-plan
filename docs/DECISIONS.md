# Decisions

- Phase 0 source specification: use `plan.md` because the required `docs/roadmap.md` is absent; its stack, roadmap phases, and success criteria are the available project specification.
  Reason: preserve the supplied project scope while making the missing-source deviation explicit.
- Phase 0 scope: create a minimal runnable scaffold and defer domain services to their named phases.
  Reason: the operating manual requires strict phase order and verified small steps.
- Frontend dependencies remain on the roadmap's Next.js 14 line for Phase 0, with a follow-up security upgrade required before release.
  Reason: the verified npm build succeeds, but npm reports one high and one critical advisory for Next.js 14.2.24.
- Finnhub connector is credential-gated; the configured token was verified with a successful live smoke test.
  Reason: the earlier unauthorized response is preserved as a fixture, while the authenticated path now proves the real success schema.
- FRED scheduled ingestion falls back to the verified bounded fixture when the provider transport disconnects.
  Reason: FRED live requests are intermittently unavailable in this environment; the parser and live endpoint remain tested independently, and scheduled ingestion stays deterministic.
- Phase 2 uses pure Python transforms rather than pandas.
  Reason: pandas is not installed in the verified environment, and the required cleaning/features are small deterministic operations with no dataframe dependency.
- Dataset versions use canonical JSON plus SHA-256 and a manifest named by the resulting content hash.
  Reason: unchanged normalized input must produce the same reproducible identifier without assuming DVC is installed.
- Phase 3 split policy is chronological 60% train, 20% validation, 20% test with no shuffling.
  Reason: financial time series must not expose future observations to training or validation; the split utility is implemented before model code.
- Phase 3 benchmarks use scikit-learn 1.8.0, joblib 1.5.3, and numpy 2.4.4, pinned in backend requirements.
  Reason: these are the verified installed versions used to generate the committed artifacts and measured metrics.
- Phase 3 models are recorded but not promoted to production when the real fixture corpus is too small, weakly labeled, or fails to beat baseline.
  Reason: five Yahoo bars and 20 RSS titles support reproducible smoke benchmarks, not defensible investment models; each metrics.json contains the measured result and ship decision.
- Phase 4 uses deterministic 256-dimensional HashingVectorizer embeddings locally instead of assuming an external embedding API key.
  Reason: it provides reproducible pgvector retrieval in the verified environment; the measured precision@1 is recorded as 4/5 rather than assumed perfect.
- Phase 4 answers are retrieval evidence plus citations, not unconstrained generated prose.
  Reason: the roadmap requires refusal when no retrieved chunk can support an answer.
- Phase 5 specialist agents use deterministic source-backed analysis until an external LLM is explicitly configured.
  Reason: all eight agents can be tested against real local state without fabricating model outputs; evidence and disagreements remain visible.
- Phase 6 explainability schema: shared Pydantic AgentResponse with required fields (evidence, confidence, sources, assumptions, limitations) enforced across all 8 agents; stance optional for agents without directional views (financial_statement, macro_economy).
  Reason: avoids each agent inventing its own response shape; test suite validates schema compliance and non-empty fields on real responses.
- Phase 6 confidence scores derived from real signals: retrieval similarity for financial_statement, sentiment aggregation for news_intelligence, verified quote confidence for valuation, documented sample size for risk, price change magnitude for technical_analysis, data sufficiency for portfolio, FRED observation quality for macro_economy.
  Reason: roadmap requires "confidence (a real computed score, not a placeholder)" — each agent's confidence now reflects its actual evidence quality.
- Phase 7 frontend uses Next.js 14 App Router with client-side fetch to FastAPI backend; all 8 pages built and wired to live endpoints.
  Reason: matches roadmap stack; static build verified; no mock data after real endpoints available.
- Phase 7 AI Chat page implements simulated streaming by sequentially rendering agent results from /orchestrate.
  Reason: true SSE/websocket streaming requires backend modification; simulated streaming demonstrates UX pattern and works with current API.
- Phase 9 CI/CD uses GitHub Actions with separate jobs for backend tests (with postgres/redis services), frontend build, Docker image build/push to GHCR, and optional Render/Vercel deploy triggers.
  Reason: standard CI/CD pattern; decouples test/build from deploy; uses service containers for realistic integration tests.
- Phase 9 production Docker Compose includes 6 services: postgres (pgvector), redis, backend, frontend, prometheus, grafana with healthchecks and named volumes.
  Reason: self-contained production stack; prometheus scrapes /metrics from backend; grafana pre-provisioned with dashboard.
- Phase 9 Prometheus metrics: custom counters/histograms/gauges for HTTP requests, orchestration latency, agent confidence; exposed at /metrics.
  Reason: roadmap requires "one Grafana panel showing real, non-zero data"; these metrics provide observable signals for monitoring.

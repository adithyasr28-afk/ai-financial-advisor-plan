# Product Requirements Document

## Product

AI Financial Advisor SaaS: a local-first financial operating system combining CA accounting, CFA portfolio analytics, personal CFO intelligence, and explainable multi-agent research.

## Objectives

- Deliver a production-grade AI-powered financial operating system for local deployment.
- Combine double-entry accounting, portfolio analytics, proactive CFO intelligence, RAG, and a multi-agent system.
- Provide explainable recommendations with evidence, confidence, guardrails, and human approval for consequential actions.

## In scope

- FastAPI backend, Next.js dashboard, PostgreSQL with pgvector, Redis, ChromaDB, Docker Compose, and GitHub Actions.
- Financial data ingestion, accounting and tax engines, portfolio analytics, ML/RAG pipelines, multi-agent research, explainability, evaluation, and deployment as defined by the roadmap.

## Out of scope for the core roadmap

- Stretch capabilities such as knowledge graph, MCP integration, RL portfolio optimization, mobile app, multi-user collaboration, paper trading, broker integrations, and voice assistant until the core phases are complete.

## Success metrics

The roadmap's stated technical, CA/CFA, and user-experience criteria are the source of truth: API p95 latency <500ms; AI recommendation latency <5s; portfolio update latency <2s; test coverage >85%; zero critical/high security vulnerabilities; backend image <2GB; frontend image <1GB; balanced trial balance; tax calculations matching the government portal; custodian performance variance <1bp; Sharpe improvement >10%; categorization accuracy >95%; GIPS-compliant reports; onboarding <5 minutes; daily active use >10 minutes; NPS >50; support tickets <5% of users/month; mobile usability >90%.


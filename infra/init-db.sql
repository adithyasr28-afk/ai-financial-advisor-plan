-- Database initialization for AI Financial Advisor
-- Run as postgres superuser

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables for ingestion records
CREATE TABLE IF NOT EXISTS ingestion_records (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ingestion_records_source ON ingestion_records(source);
CREATE INDEX IF NOT EXISTS idx_ingestion_records_ingested_at ON ingestion_records(ingested_at);

-- Create tables for RAG chunks
-- NOTE: this must stay in sync with backend/rag/store.py::ensure_schema(),
-- which is the schema the application code actually reads/writes against.
-- chunk_id is the primary key (not a separate surrogate id) because
-- upsert_chunks() relies on ON CONFLICT (chunk_id) DO UPDATE.
CREATE TABLE IF NOT EXISTS rag_chunks (
    chunk_id TEXT PRIMARY KEY,
    source_file TEXT NOT NULL,
    chunk_index INT NOT NULL,
    section TEXT,
    content TEXT NOT NULL,
    embedding VECTOR(256) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding ON rag_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create tables for market data
CREATE TABLE IF NOT EXISTS market_bars (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume BIGINT NOT NULL,
    source VARCHAR(50) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (symbol, timestamp, source)
);

CREATE INDEX IF NOT EXISTS idx_market_bars_symbol_timestamp ON market_bars(symbol, timestamp DESC);

-- Create tables for macro data
CREATE TABLE IF NOT EXISTS macro_observations (
    id BIGSERIAL PRIMARY KEY,
    series_id VARCHAR(50) NOT NULL,
    observation_date DATE NOT NULL,
    value DECIMAL(20, 6) NOT NULL,
    source VARCHAR(50) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (series_id, observation_date)
);

CREATE INDEX IF NOT EXISTS idx_macro_observations_series_date ON macro_observations(series_id, observation_date DESC);

-- Create tables for news
CREATE TABLE IF NOT EXISTS news_items (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    published_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (link)
);

CREATE INDEX IF NOT EXISTS idx_news_items_published_at ON news_items(published_at DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
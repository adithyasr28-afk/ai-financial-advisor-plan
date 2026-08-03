# Phase 4 Retrieval Run

- Corpus: 3 real SEC EDGAR Apple 10-K HTML filings from 2023, 2024, and 2025.
- Ingested chunks: 512.
- Storage: PostgreSQL 15 with pgvector 0.8.5.
- Embedding: deterministic 256-dimensional HashingVectorizer.
- Queries evaluated: 5.
- Precision@1: 4/5 (0.80), measured by expected-term presence in the retrieved source chunk.
- Citation contract: every non-refused response includes `chunk_id`, `source_file`, `chunk_index`, and similarity; empty retrieval refuses to answer.

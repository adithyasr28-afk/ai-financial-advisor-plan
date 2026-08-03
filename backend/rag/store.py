from collections.abc import Iterable
from typing import Any
import psycopg

from .documents import DocumentChunk
from .embeddings import EMBEDDING_DIMENSIONS, embed_text, embed_texts, vector_literal


def ensure_schema(connection: psycopg.Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS rag_chunks (chunk_id TEXT PRIMARY KEY, source_file TEXT NOT NULL, chunk_index INTEGER NOT NULL, section TEXT, content TEXT NOT NULL, embedding vector({EMBEDDING_DIMENSIONS}) NOT NULL, metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb)")
    connection.commit()


def upsert_chunks(connection: psycopg.Connection, chunks: Iterable[DocumentChunk]) -> int:
    materialized = list(chunks)
    vectors = embed_texts([chunk.text for chunk in materialized])
    with connection.cursor() as cursor:
        for chunk, vector in zip(materialized, vectors, strict=True):
            cursor.execute("INSERT INTO rag_chunks (chunk_id, source_file, chunk_index, section, content, embedding, metadata) VALUES (%s, %s, %s, %s, %s, %s::vector, %s::jsonb) ON CONFLICT (chunk_id) DO UPDATE SET content=EXCLUDED.content, embedding=EXCLUDED.embedding, metadata=EXCLUDED.metadata", (chunk.chunk_id, chunk.source_file, chunk.chunk_index, chunk.section, chunk.text, vector_literal(vector), "{}"))
    connection.commit()
    return len(materialized)


def retrieve(connection: psycopg.Connection, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    vector = vector_literal(embed_text(query))
    with connection.cursor() as cursor:
        cursor.execute("SELECT chunk_id, source_file, chunk_index, section, content, 1 - (embedding <=> %s::vector) AS similarity FROM rag_chunks ORDER BY embedding <=> %s::vector LIMIT %s", (vector, vector, top_k))
        columns = [description.name for description in cursor.description]
        return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]

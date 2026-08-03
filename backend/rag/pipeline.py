import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

from .documents import chunks_from_file
from .store import ensure_schema, retrieve, upsert_chunks


def ingest_directory(database_url: str, directory: Path) -> int:
    files = sorted(directory.glob("*.htm"))
    with psycopg.connect(database_url) as connection:
        ensure_schema(connection)
        total = 0
        for path in files:
            total += upsert_chunks(connection, chunks_from_file(path))
    return total


def cited_answer(database_url: str, query: str, top_k: int = 5) -> dict:
    with psycopg.connect(database_url) as connection:
        matches = retrieve(connection, query, top_k)
    if not matches:
        return {"answer": None, "citations": [], "refused": True, "reason": "No retrieved source chunk supports this question."}
    citations = [{"chunk_id": match["chunk_id"], "source_file": match["source_file"], "chunk_index": match["chunk_index"], "similarity": float(match["similarity"])} for match in matches]
    return {"answer": "Retrieved evidence only; synthesize an answer from the cited chunks.", "evidence": [match["content"] for match in matches], "citations": citations, "refused": False}


if __name__ == "__main__":
    root = Path(__file__).parents[2]
    load_dotenv(root / "backend" / ".env")
    url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_financial_advisor")
    print(f"ingested {ingest_directory(url, root / 'fixtures' / 'annual_reports')} chunks")

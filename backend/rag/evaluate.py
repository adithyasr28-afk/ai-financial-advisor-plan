import json
import os
from pathlib import Path
from dotenv import load_dotenv

from .pipeline import cited_answer


QUERIES = {
    "net sales": ["net sales"],
    "cash and cash equivalents": ["cash"],
    "risk factors": ["risk"],
    "research and development": ["research and development"],
    "operating segments": ["operating segment"],
}


def evaluate(database_url: str, top_k: int = 1) -> dict:
    results = []
    for query, expected_terms in QUERIES.items():
        response = cited_answer(database_url, query, top_k)
        evidence = " ".join(response.get("evidence", [])).lower()
        relevant = any(term in evidence for term in expected_terms)
        results.append({"query": query, "relevant_at_k": relevant, "citations": response["citations"]})
    return {"k": top_k, "queries": results, "relevant_count": sum(item["relevant_at_k"] for item in results), "precision_at_k": sum(item["relevant_at_k"] for item in results) / len(results)}


if __name__ == "__main__":
    root = Path(__file__).parents[2]
    load_dotenv(root / "backend" / ".env")
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_financial_advisor")
    print(json.dumps(evaluate(database_url), indent=2))

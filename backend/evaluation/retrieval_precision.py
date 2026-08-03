#!/usr/bin/env python
"""Retrieval precision evaluation - measures precision@k for RAG queries."""

import json
import statistics
from pathlib import Path
from typing import Any

from backend.rag.pipeline import cited_answer
from backend.agents.system import AgentContext


# Known correct answers for test queries (source file should contain the answer)
TEST_QUERIES = [
    {"query": "Apple net sales 2025", "expected_source": "apple_2025_10k.htm"},
    {"query": "Apple revenue 2024", "expected_source": "apple_2024_10k.htm"},
    {"query": "Apple cash flow 2023", "expected_source": "apple_2023_10k.htm"},
    {"query": "Apple total assets", "expected_source": "apple_2025_10k.htm"},
    {"query": "Apple research and development expenses", "expected_source": "apple_2025_10k.htm"},
]


def run_retrieval_precision(top_k: int = 3) -> dict:
    context = AgentContext.from_project()

    results = []
    for test in TEST_QUERIES:
        answer = cited_answer(context.database_url, test["query"], top_k)
        if answer["refused"]:
            results.append({
                "query": test["query"],
                "refused": True,
                "precision_at_k": 0.0,
                "expected_source": test["expected_source"],
            })
            continue

        # Check if expected source appears in top-k citations
        found = False
        for citation in answer["citations"]:
            if test["expected_source"] in citation["source_file"]:
                found = True
                break

        precision = 1.0 if found else 0.0
        results.append({
            "query": test["query"],
            "refused": False,
            "precision_at_k": precision,
            "expected_source": test["expected_source"],
            "retrieved_sources": [c["source_file"] for c in answer["citations"]],
        })

    avg_precision = statistics.mean(r["precision_at_k"] for r in results)
    return {
        "metric": "retrieval_precision_at_k",
        "top_k": top_k,
        "samples": len(results),
        "average_precision": avg_precision,
        "per_query": results,
    }


if __name__ == "__main__":
    result = run_retrieval_precision(3)
    print(json.dumps(result, indent=2))

    eval_path = Path(__file__).parents[2] / "docs" / "EVAL_RESULTS.md"
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Retrieval Precision@k\n")
        f.write(f"- **Top-K**: {result['top_k']}\n")
        f.write(f"- **Samples**: {result['samples']}\n")
        f.write(f"- **Average Precision@{result['top_k']}**: {result['average_precision']:.2%}\n")
        f.write(f"- **Details**:\n")
        for r in result["per_query"]:
            status = "refused" if r["refused"] else ("hit" if r["precision_at_k"] == 1.0 else "miss")
            f.write(f"  - Query: `{r['query']}` | Expected: {r['expected_source']} | Retrieved: {r.get('retrieved_sources', [])} | {status}\n")
#!/usr/bin/env python
"""Hallucination rate evaluation - samples agent answers and checks citation validity."""

import json
import statistics
from pathlib import Path
from typing import Any

from backend.agents.system import AgentContext, orchestrate


def check_citation_validity(evidence: list[dict[str, Any]]) -> tuple[int, int]:
    """Check if citations have valid source references. Returns (valid, total)."""
    if not evidence:
        return 0, 0
    valid = 0
    for e in evidence:
        has_source = bool(e.get("source"))
        has_content = any(
            v for k, v in e.items()
            if k not in ("source", "chunk_id", "source_file", "sentiment_score", "entities", "metrics")
            and v is not None
        )
        if has_source and has_content:
            valid += 1
    return valid, len(evidence)


def run_hallucination_eval(num_samples: int = 20) -> dict:
    context = AgentContext.from_project()
    queries = [
        "latest news for Apple",
        "AAPL comprehensive report",
        "Apple revenue 2025",
        "IBM valuation",
        "portfolio risk assessment",
        "AAPL technical analysis trend",
        "my portfolio holdings",
        "current GDP macro economy",
        "Apple stock news",
        "financial statement analysis",
    ]

    results = []
    for i in range(min(num_samples, len(queries) * 2)):
        query = queries[i % len(queries)]
        result = orchestrate(context, query)

        total_valid = 0
        total_evidence = 0
        for agent_result in result["results"]:
            valid, total = check_citation_validity(agent_result["evidence"])
            total_valid += valid
            total_evidence += total

        hallucination_rate = 1 - (total_valid / total_evidence) if total_evidence > 0 else 0
        results.append({
            "query": query,
            "agents": result["agents"],
            "total_evidence": total_evidence,
            "valid_citations": total_valid,
            "hallucination_rate": hallucination_rate,
        })

    avg_rate = statistics.mean(r["hallucination_rate"] for r in results)
    return {
        "metric": "hallucination_rate",
        "samples": len(results),
        "average_hallucination_rate": avg_rate,
        "per_query": results,
    }


if __name__ == "__main__":
    result = run_hallucination_eval(20)
    print(json.dumps(result, indent=2))

    # Write to EVAL_RESULTS.md
    eval_path = Path(__file__).parents[2] / "docs" / "EVAL_RESULTS.md"
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Hallucination Rate\n")
        f.write(f"- **Samples**: {result['samples']}\n")
        f.write(f"- **Average Hallucination Rate**: {result['average_hallucination_rate']:.2%}\n")
        f.write(f"- **Details**:\n")
        for r in result["per_query"]:
            f.write(f"  - Query: `{r['query']}` | Agents: {r['agents']} | Evidence: {r['total_evidence']} | Valid: {r['valid_citations']} | Rate: {r['hallucination_rate']:.2%}\n")
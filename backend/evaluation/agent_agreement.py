#!/usr/bin/env python
"""Agent agreement evaluation - measures how often agents agree/disagree."""

import json
from collections import Counter
from pathlib import Path
from typing import Any

from backend.agents.system import AgentContext, orchestrate


def run_agent_agreement_eval(num_queries: int = 10) -> dict:
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
        "tech sector outlook",
        "market risk today",
    ]

    results = []
    stance_counts = Counter()

    for query in queries[:num_queries]:
        result = orchestrate(context, query)
        stances = []
        for agent_result in result["results"]:
            stance = agent_result.get("stance")
            if stance:
                stances.append(stance)
                stance_counts[stance] += 1

        # Agreement: all non-None stances are the same
        unique_stances = set(stances)
        agreement = len(unique_stances) <= 1 if stances else None

        results.append({
            "query": query,
            "agents": result["agents"],
            "stances": stances,
            "unique_stances": list(unique_stances),
            "agreement": agreement,
            "has_disagreement": len(result.get("disagreements", [])) > 0,
        })

    total_with_stances = sum(1 for r in results if r["agreement"] is not None)
    agreements = sum(1 for r in results if r["agreement"] is True)
    disagreements = sum(1 for r in results if r["agreement"] is False)

    return {
        "metric": "agent_agreement",
        "queries": num_queries,
        "total_with_stances": total_with_stances,
        "agreement_count": agreements,
        "disagreement_count": disagreements,
        "agreement_rate": agreements / total_with_stances if total_with_stances > 0 else 0,
        "stance_distribution": dict(stance_counts),
        "per_query": results,
    }


if __name__ == "__main__":
    result = run_agent_agreement_eval(10)
    print(json.dumps(result, indent=2))

    eval_path = Path(__file__).parents[2] / "docs" / "EVAL_RESULTS.md"
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Agent Agreement\n")
        f.write(f"- **Queries Tested**: {result['queries']}\n")
        f.write(f"- **With Stances**: {result['total_with_stances']}\n")
        f.write(f"- **Agreements**: {result['agreement_count']}\n")
        f.write(f"- **Disagreements**: {result['disagreement_count']}\n")
        f.write(f"- **Agreement Rate**: {result['agreement_rate']:.1%}\n")
        f.write(f"- **Stance Distribution**: {json.dumps(result['stance_distribution'])}\n")
        f.write(f"- **Details**:\n")
        for r in result["per_query"]:
            status = "agree" if r["agreement"] else ("disagree" if r["agreement"] is False else "no_stance")
            f.write(f"  - Query: `{r['query']}` | Stances: {r['stances']} | {status}\n")
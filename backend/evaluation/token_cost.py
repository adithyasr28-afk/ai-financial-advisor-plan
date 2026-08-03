#!/usr/bin/env python
"""Token cost evaluation - estimates token usage for agent responses."""

import json
import tiktoken
from pathlib import Path
from typing import Any

from backend.agents.system import AgentContext, orchestrate


# Approximate token costs (as of 2024, using gpt-4o-mini pricing)
# Input: $0.15/1M tokens, Output: $0.60/1M tokens
INPUT_COST_PER_1M = 0.15
OUTPUT_COST_PER_1M = 0.60


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def estimate_cost(query: str, response: dict[str, Any]) -> dict:
    input_tokens = count_tokens(query)
    response_str = json.dumps(response)
    output_tokens = count_tokens(response_str)

    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_1M
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_1M

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_usd": input_cost,
        "output_cost_usd": output_cost,
        "total_cost_usd": input_cost + output_cost,
    }


def run_token_cost_eval(num_samples: int = 5) -> dict:
    context = AgentContext.from_project()
    queries = [
        "latest news for Apple",
        "AAPL comprehensive report",
        "Apple revenue 2025",
        "IBM valuation",
        "portfolio risk assessment",
    ]

    results = []
    for query in queries[:num_samples]:
        response = orchestrate(context, query)
        cost = estimate_cost(query, response)
        cost["query"] = query
        cost["agents_invoked"] = len(response["agents"])
        results.append(cost)

    avg_tokens = sum(r["total_tokens"] for r in results) / len(results)
    avg_cost = sum(r["total_cost_usd"] for r in results) / len(results)

    return {
        "metric": "token_cost",
        "model": "gpt-4o-mini (estimated)",
        "pricing": {"input_per_1m": INPUT_COST_PER_1M, "output_per_1m": OUTPUT_COST_PER_1M},
        "samples": len(results),
        "average_tokens": round(avg_tokens),
        "average_cost_usd": round(avg_cost, 6),
        "per_query": results,
    }


if __name__ == "__main__":
    result = run_token_cost_eval(5)
    print(json.dumps(result, indent=2))

    eval_path = Path(__file__).parents[2] / "docs" / "EVAL_RESULTS.md"
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Token Cost (Estimated)\n")
        f.write(f"- **Model**: {result['model']}\n")
        f.write(f"- **Pricing**: Input ${result['pricing']['input_per_1m']}/1M, Output ${result['pricing']['output_per_1m']}/1M\n")
        f.write(f"- **Samples**: {result['samples']}\n")
        f.write(f"- **Average Tokens**: {result['average_tokens']}\n")
        f.write(f"- **Average Cost**: ${result['average_cost_usd']:.6f}\n")
        f.write(f"- **Details**:\n")
        for r in result["per_query"]:
            f.write(f"  - Query: `{r['query']}` | Agents: {r['agents_invoked']} | Tokens: {r['total_tokens']} (in:{r['input_tokens']}/out:{r['output_tokens']}) | Cost: ${r['total_cost_usd']:.6f}\n")
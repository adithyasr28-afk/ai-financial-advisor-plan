#!/usr/bin/env python
"""Latency evaluation - measures end-to-end latency for agent orchestration."""

import json
import statistics
import time
from pathlib import Path
from typing import Any

from backend.agents.system import AgentContext, orchestrate


def run_latency_eval(num_runs: int = 10) -> dict:
    context = AgentContext.from_project()
    queries = [
        "latest news for Apple",
        "AAPL comprehensive report",
        "Apple revenue 2025",
        "IBM valuation",
        "portfolio risk assessment",
    ]

    latencies = []
    per_query = []

    for i in range(num_runs):
        query = queries[i % len(queries)]
        start = time.perf_counter()
        _ = orchestrate(context, query)
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)
        per_query.append({"query": query, "latency_ms": round(elapsed * 1000, 2)})

    return {
        "metric": "latency",
        "runs": num_runs,
        "mean_ms": round(statistics.mean(latencies) * 1000, 2),
        "median_ms": round(statistics.median(latencies) * 1000, 2),
        "stdev_ms": round(statistics.stdev(latencies) * 1000, 2) if len(latencies) > 1 else 0,
        "min_ms": round(min(latencies) * 1000, 2),
        "max_ms": round(max(latencies) * 1000, 2),
        "per_query": per_query,
    }


if __name__ == "__main__":
    result = run_latency_eval(10)
    print(json.dumps(result, indent=2))

    eval_path = Path(__file__).parents[2] / "docs" / "EVAL_RESULTS.md"
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Latency\n")
        f.write(f"- **Runs**: {result['runs']}\n")
        f.write(f"- **Mean**: {result['mean_ms']} ms\n")
        f.write(f"- **Median**: {result['median_ms']} ms\n")
        f.write(f"- **Std Dev**: {result['stdev_ms']} ms\n")
        f.write(f"- **Min**: {result['min_ms']} ms\n")
        f.write(f"- **Max**: {result['max_ms']} ms\n")
#!/usr/bin/env python
"""Forecast accuracy evaluation - evaluates ML model predictions against actuals."""

import json
import statistics
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from backend.agents.system import AgentContext
from backend.data_engineering.features import simple_returns
from backend.ingestion.connectors.yahoo import parse_fixture


def run_forecast_accuracy_eval() -> dict:
    context = AgentContext.from_project()

    # Load the forecasting model
    model_path = context.root / "models" / "forecasting" / "model.joblib"
    metrics_path = context.root / "models" / "forecasting" / "metrics.json"

    if not model_path.exists():
        return {
            "metric": "forecast_accuracy",
            "status": "no_model",
            "message": "No forecasting model artifact found",
        }

    model = joblib.load(model_path)

    # Load metrics for reference
    with open(metrics_path, "r") as f:
        training_metrics = json.load(f)

    # Get real market data for evaluation
    bars = parse_fixture(context.root / "fixtures" / "yahoo_sample.json")
    if len(bars) < 2:
        return {
            "metric": "forecast_accuracy",
            "status": "insufficient_data",
            "message": "Not enough bars for forecast evaluation",
        }

    # Use returns as features (simple evaluation)
    returns = simple_returns(bars)

    # Prepare features: use last N returns as input
    window = 5
    X, y = [], []
    # Filter out None values
    valid_returns = [r for r in returns if r is not None]
    for i in range(window, len(valid_returns)):
        X.append(valid_returns[i-window:i])
        y.append(valid_returns[i])

    if len(X) == 0:
        return {
            "metric": "forecast_accuracy",
            "status": "insufficient_data",
            "message": "Not enough data points for window",
        }

    X = np.array(X)
    y = np.array(y)

    # Predict
    preds = model.predict(X)

    # Metrics
    mae = np.mean(np.abs(preds - y))
    rmse = np.sqrt(np.mean((preds - y) ** 2))
    mape = np.mean(np.abs((y - preds) / np.where(y != 0, y, 1))) * 100

    # Directional accuracy
    direction_correct = np.sum((preds > 0) == (y > 0))
    directional_accuracy = direction_correct / len(y) * 100

    return {
        "metric": "forecast_accuracy",
        "status": "evaluated",
        "training_metrics": training_metrics,
        "test_samples": len(y),
        "mae": float(mae),
        "rmse": float(rmse),
        "mape_percent": float(mape),
        "directional_accuracy_percent": float(directional_accuracy),
        "predictions": preds.tolist(),
        "actuals": y.tolist(),
    }


if __name__ == "__main__":
    result = run_forecast_accuracy_eval()
    print(json.dumps(result, indent=2))

    eval_path = Path(__file__).parents[2] / "docs" / "EVAL_RESULTS.md"
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Forecast Accuracy\n")
        if result["status"] != "evaluated":
            f.write(f"- **Status**: {result['status']}\n")
            f.write(f"- **Message**: {result['message']}\n")
        else:
            f.write(f"- **Test Samples**: {result['test_samples']}\n")
            f.write(f"- **MAE**: {result['mae']:.6f}\n")
            f.write(f"- **RMSE**: {result['rmse']:.6f}\n")
            f.write(f"- **MAPE**: {result['mape_percent']:.2f}%\n")
            f.write(f"- **Directional Accuracy**: {result['directional_accuracy_percent']:.1f}%\n")
            f.write(f"- **Training Metrics**: {json.dumps(result['training_metrics'])}\n")
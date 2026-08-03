"""Run the Phase 3 classical-ML benchmarks on the verified Phase 1 fixtures."""
import json
import math
import re
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import f1_score, mean_absolute_error, mean_squared_error, roc_auc_score
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.dummy import DummyClassifier

from backend.ingestion.connectors.gnews import parse_fixture
from backend.ingestion.connectors.yahoo import parse_fixture as parse_yahoo
from backend.ml.splits import chronological_split


def _write(output: Path, name: str, metrics: dict[str, Any], model: Any) -> None:
    directory = output / name
    directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, directory / "model.joblib")
    (directory / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _metric_pair(actual: list[float], predicted: list[float]) -> dict[str, float]:
    return {"mae": mean_absolute_error(actual, predicted), "rmse": math.sqrt(mean_squared_error(actual, predicted))}


def run_forecasting(fixtures: Path, output: Path) -> dict[str, Any]:
    bars = parse_yahoo(fixtures / "yahoo_sample.json")
    closes = [bar.close for bar in bars]
    split = chronological_split(closes)
    train_end = len(split.train)
    test_start = train_end + len(split.validation)
    model = LinearRegression().fit(np.arange(train_end).reshape(-1, 1), np.array(split.train))
    actual = closes[test_start:]
    target_prediction = model.predict(np.arange(test_start, len(closes)).reshape(-1, 1)).tolist()
    baseline_prediction = [split.train[-1]] * len(actual)
    metrics = {"task": "forecasting", "metric": "MAE/RMSE", "baseline": _metric_pair(actual, baseline_prediction), "target": _metric_pair(actual, target_prediction), "sample_count": len(closes), "ship_decision": "hold: five observations are insufficient for a production forecast"}
    _write(output, "forecasting", metrics, model)
    return metrics


def _weak_sentiment(title: str) -> int:
    """Weak labels are explicit and are not presented as ground truth."""
    positive = ("pay off", "winner", "beating", "higher", "buy", "bought", "trillion")
    negative = ("bad news", "spooking", "worrying", "undercut", "unlikely", "last earnings")
    lowered = title.lower()
    return -1 if any(word in lowered for word in negative) else 1 if any(word in lowered for word in positive) else 0


def run_sentiment(fixtures: Path, output: Path) -> dict[str, Any]:
    titles = [item.title for item in parse_fixture(fixtures / "gnews_sample.xml") if item.title != "Yahoo! Finance: AAPL News"]
    labels = [_weak_sentiment(title) for title in titles]
    split = chronological_split(list(zip(titles, labels)))
    train_text, train_y = zip(*split.train)
    test_text, test_y = zip(*split.test)
    target = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000, random_state=42))
    if len(set(train_y)) < 2:
        target = DummyClassifier(strategy="most_frequent")
    target.fit(train_text, train_y)
    baseline = [max(set(train_y), key=train_y.count)] * len(test_y)
    predicted = target.predict(test_text).tolist()
    metrics = {"task": "sentiment", "metric": "weighted F1", "baseline": {"f1": f1_score(test_y, baseline, average="weighted", zero_division=0)}, "target": {"f1": f1_score(test_y, predicted, average="weighted", zero_division=0)}, "sample_count": len(titles), "label_source": "weak keyword labels from real RSS titles", "ship_decision": "hold: labels are weakly supervised and require human-labeled news before production use"}
    _write(output, "sentiment", metrics, target)
    return metrics


def run_anomaly(fixtures: Path, output: Path) -> dict[str, Any]:
    bars = parse_yahoo(fixtures / "yahoo_sample.json")
    closes = np.array([bar.close for bar in bars])
    returns = np.diff(closes) / closes[:-1]
    features = np.column_stack((returns, np.array([bar.volume for bar in bars[1:]], dtype=float)))
    split = chronological_split(list(range(len(features))))
    train_n = len(split.train)
    threshold = abs(returns[:train_n]).mean() + 2 * abs(returns[:train_n]).std()
    actual = (abs(returns[train_n:]) > threshold).astype(int)
    baseline = np.zeros(len(actual), dtype=int)
    model = IsolationForest(n_estimators=100, contamination="auto", random_state=42).fit(features[:train_n])
    predicted = (model.predict(features[train_n:]) == -1).astype(int)
    metrics = {"task": "anomaly_detection", "metric": "F1", "baseline": {"f1": f1_score(actual, baseline, zero_division=0)}, "target": {"f1": f1_score(actual, predicted, zero_division=0)}, "sample_count": len(features), "ship_decision": "hold: four return observations cannot establish a reliable anomaly threshold"}
    _write(output, "anomaly_detection", metrics, model)
    return metrics


def _entities(title: str) -> set[str]:
    known = {"apple", "nvidia", "tesla", "qualcomm", "ford", "coca-cola", "samsung", "vti", "china"}
    lowered = title.lower()
    return {entity for entity in known if entity in lowered}


def run_similarity(fixtures: Path, output: Path) -> dict[str, Any]:
    titles = [item.title for item in parse_fixture(fixtures / "gnews_sample.xml") if _entities(item.title)]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(titles)
    model = NearestNeighbors(n_neighbors=min(2, len(titles)), metric="cosine").fit(matrix)
    neighbors = model.kneighbors(matrix, return_distance=False)
    hits = 0
    evaluated = 0
    for index, row in enumerate(neighbors):
        if len(row) < 2:
            continue
        evaluated += 1
        hits += bool(_entities(titles[index]) & _entities(titles[row[1]]))
    target_rate = hits / evaluated if evaluated else 0.0
    most_common = max((len(_entities(title)) for title in titles), default=0)
    baseline_rate = sum(bool(_entities(title)) and len(_entities(title)) >= most_common for title in titles) / len(titles) if titles else 0.0
    metrics = {"task": "company_similarity", "metric": "top-1 shared-entity rate", "baseline": {"rate": baseline_rate}, "target": {"rate": target_rate}, "sample_count": len(titles), "ship_decision": "hold: RSS-title corpus is not a validated company-document similarity benchmark"}
    _write(output, "company_similarity", metrics, {"vectorizer": vectorizer, "nearest_neighbors": model})
    return metrics


def run_risk(fixtures: Path, output: Path) -> dict[str, Any]:
    bars = parse_yahoo(fixtures / "yahoo_sample.json")
    closes = np.array([bar.close for bar in bars])
    returns = np.diff(closes) / closes[:-1]
    features = np.column_stack((abs(returns[:-1]), np.array([bar.volume for bar in bars[1:-1]], dtype=float)))
    labels = (abs(returns[1:]) > np.median(abs(returns[:2]))).astype(int)
    split = chronological_split(list(range(len(features))))
    train_n = len(split.train)
    if len(set(labels[:train_n])) < 2:
        model = DummyClassifier(strategy="most_frequent").fit(features[:train_n], labels[:train_n])
    else:
        model = LogisticRegression(random_state=42).fit(features[:train_n], labels[:train_n])
    baseline = np.full(len(labels[train_n:]), int(round(labels[:train_n].mean())))
    predicted = model.predict(features[train_n:])
    actual = labels[train_n:]
    target_metrics = {"f1": f1_score(actual, predicted, zero_division=0)}
    if len(set(actual)) > 1:
        target_metrics["roc_auc"] = roc_auc_score(actual, model.predict_proba(features[train_n:])[:, 1])
    else:
        target_metrics["roc_auc"] = None
    metrics = {"task": "risk_prediction", "metric": "F1/ROC-AUC", "baseline": {"f1": f1_score(actual, baseline, zero_division=0)}, "target": target_metrics, "sample_count": len(features), "ship_decision": "hold: test labels are too few for a reliable risk model"}
    _write(output, "risk_prediction", metrics, model)
    return metrics


def run_all(root: Path) -> dict[str, Any]:
    fixtures = root / "fixtures"
    output = root / "models"
    results = {"forecasting": run_forecasting(fixtures, output), "sentiment": run_sentiment(fixtures, output), "anomaly_detection": run_anomaly(fixtures, output), "company_similarity": run_similarity(fixtures, output), "risk_prediction": run_risk(fixtures, output)}
    (output / "metrics.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    root = Path(__file__).parents[2]
    print(json.dumps(run_all(root), indent=2, sort_keys=True))

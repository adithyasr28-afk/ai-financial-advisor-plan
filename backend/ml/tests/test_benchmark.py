import json

from backend.ml.benchmark import run_all


def test_all_model_benchmarks_write_artifacts(tmp_path):
    root = tmp_path
    fixtures = root / "fixtures"
    real_fixtures = __import__("pathlib").Path(__file__).parents[3] / "fixtures"
    fixtures.mkdir()
    for source in real_fixtures.iterdir():
        if source.is_file():
            (fixtures / source.name).write_bytes(source.read_bytes())
    results = run_all(root)
    assert set(results) == {"forecasting", "sentiment", "anomaly_detection", "company_similarity", "risk_prediction"}
    for name in results:
        directory = root / "models" / name
        assert (directory / "model.joblib").exists()
        metrics = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
        assert "baseline" in metrics and "target" in metrics

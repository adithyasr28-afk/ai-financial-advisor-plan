from backend.ingestion.scheduler import collect_fixture_records


def test_scheduler_collects_fixture_records():
    from pathlib import Path
    records = collect_fixture_records(Path(__file__).parents[3] / "fixtures")
    assert len(records) > 10
    assert {record["source"] for record in records} == {"yahoo_finance", "alpha_vantage", "sec_edgar", "fred", "rss"}

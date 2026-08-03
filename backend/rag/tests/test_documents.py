from pathlib import Path

from backend.rag.documents import chunks_from_file


def test_real_annual_report_chunks_have_traceable_ids():
    path = Path(__file__).parents[3] / "fixtures" / "annual_reports" / "apple_2025_10k.htm"
    chunks = chunks_from_file(path)
    assert len(chunks) > 100
    assert chunks[0].chunk_id == "apple_2025_10k.htm:0"
    assert all(chunk.source_file == path.name for chunk in chunks[:3])

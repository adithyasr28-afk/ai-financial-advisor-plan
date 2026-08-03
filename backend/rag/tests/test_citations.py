from backend.rag.pipeline import cited_answer


def test_citation_contract_refuses_without_retrieval(monkeypatch):
    class EmptyConnection:
        pass

    monkeypatch.setattr("backend.rag.pipeline.psycopg.connect", lambda _: _empty_context())
    result = cited_answer("unused", "unanswerable query")
    assert result["refused"] is True
    assert result["citations"] == []


class _empty_context:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def cursor(self):
        return _empty_cursor()


class _empty_cursor:
    description = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, *args):
        pass

    def fetchall(self):
        return []

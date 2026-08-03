from backend.rag.embeddings import EMBEDDING_DIMENSIONS, embed_text, embed_texts


def test_embeddings_are_fixed_dimension_and_deterministic():
    first = embed_text("Apple revenue increased")
    second = embed_texts(["Apple revenue increased"])[0]
    assert len(first) == EMBEDDING_DIMENSIONS
    assert first == second

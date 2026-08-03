from collections.abc import Iterable
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

EMBEDDING_DIMENSIONS = 256
_VECTORIZER = HashingVectorizer(n_features=EMBEDDING_DIMENSIONS, alternate_sign=False, norm="l2", stop_words="english")


def embed_texts(texts: Iterable[str]) -> list[list[float]]:
    matrix = _VECTORIZER.transform(list(texts)).toarray().astype(float)
    return matrix.tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in vector) + "]"

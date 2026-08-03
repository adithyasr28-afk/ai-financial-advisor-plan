import pytest

from backend.ml.splits import chronological_split


def test_split_preserves_time_order_and_disjointness():
    split = chronological_split(list(range(10)))
    assert split.train == [0, 1, 2, 3, 4, 5]
    assert split.validation == [6, 7]
    assert split.test == [8, 9]
    assert set(split.train).isdisjoint(split.validation)
    assert set(split.validation).isdisjoint(split.test)


def test_empty_data_rejected():
    with pytest.raises(ValueError, match="empty"):
        chronological_split([])

from dataclasses import dataclass
from collections.abc import Sequence
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class TemporalSplit(Generic[T]):
    train: list[T]
    validation: list[T]
    test: list[T]


def chronological_split(records: Sequence[T], train_fraction: float = 0.6, validation_fraction: float = 0.2) -> TemporalSplit[T]:
    """Split ordered records without shuffling or allowing future leakage."""
    if not records:
        raise ValueError("records cannot be empty")
    if not (0 < train_fraction < 1 and 0 < validation_fraction < 1 and train_fraction + validation_fraction < 1):
        raise ValueError("fractions must be positive and leave a test partition")
    train_end = max(1, int(len(records) * train_fraction))
    validation_end = max(train_end + 1, int(len(records) * (train_fraction + validation_fraction)))
    validation_end = min(validation_end, len(records) - 1) if len(records) > 1 else len(records)
    return TemporalSplit(list(records[:train_end]), list(records[train_end:validation_end]), list(records[validation_end:]))

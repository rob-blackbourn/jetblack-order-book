"""Linq style functions"""

from typing import Callable, Iterable, Sequence, TypeVar

T = TypeVar('T')


def index_of(seq: Iterable[T], predicate: Callable[[T], bool]) -> int:
    return next(
        (
            index
            for index, item in enumerate(seq)
            if predicate(item)
        ),
        -1
    )


def last_index_of(seq: Sequence[T], predicate: Callable[[T], bool]) -> int:
    return index_of(reversed(seq), predicate)

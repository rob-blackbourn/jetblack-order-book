"""Linq style functions"""

from typing import Callable, Iterable, List, Sequence, TypeVar

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


def first(seq: Iterable[T], predicate: Callable[[T], bool]) -> T:
    return next(item for item in seq if predicate(item))


def where(seq: Iterable[T], predicate: Callable[[T], bool]) -> List[T]:
    return [item for item in seq if predicate(item)]


def contains(seq: Iterable[T], predicate: Callable[[T], bool]) -> bool:
    return any(predicate(item) for item in seq)

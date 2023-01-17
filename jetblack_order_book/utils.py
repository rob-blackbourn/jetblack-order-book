"""Utilities"""

from typing import Callable, Iterable, TypeVar

T = TypeVar('T')


def index_of(seq: Iterable[T], predicate: Callable[[T], bool]) -> int:
    """Find the index in a collection where the predicate is satisfied or -1.

    Args:
        seq (Iterable[T]): The collection.
        predicate (Callable[[T], bool]): The predicate.

    Returns:
        int: The index where the predicate is true or -1.
    """
    return next(
        (
            index
            for index, item in enumerate(seq)
            if predicate(item)
        ),
        -1
    )

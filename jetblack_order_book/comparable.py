"""Comparable"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod


class Comparable(metaclass=ABCMeta):

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Comparable):
            return False
        return self.compare(other) == 0

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Comparable):
            return True
        return self.compare(other) != 0

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Comparable):
            raise ValueError("object must be Comparable")
        return self.compare(other) < 0

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Comparable):
            raise ValueError("object must be Comparable")
        return self.compare(other) <= 0

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Comparable):
            raise ValueError("object must be Comparable")
        return self.compare(other) > 0

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Comparable):
            raise ValueError("object must be Comparable")
        return self.compare(other) >= 0

    @abstractmethod
    def compare(self, other: Comparable) -> int:
        ...

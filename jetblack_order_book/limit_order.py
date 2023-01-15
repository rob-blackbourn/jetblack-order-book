"""Limit Order"""

from __future__ import annotations

from decimal import Decimal

from .comparable import Comparable
from .order_types import Side


class LimitOrder(Comparable):

    def __init__(
            self,
            order_id: int,
            side: Side,
            price: Decimal,
            size: int
    ) -> None:
        self.order_id = order_id
        self.side = side
        self.price = price
        self.size = size

    def __repr__(self) -> str:
        return f"LimitOrder({self.price}, {self.size}, {self.order_id})"

    def __str__(self) -> str:
        return f"{self.price}x{self.size}"

    def __hash__(self) -> int:
        return hash((self.order_id, self.side, self.price, self.size))

    def compare(self, other: Comparable) -> int:
        assert isinstance(other, LimitOrder)

        if self.side > other.side:
            return 1
        elif self.side < other.side:
            return -1
        elif self.price > other.price:
            return 1
        elif self.price < other.price:
            return -1
        elif self.size > other.size:
            return 1
        elif self.size < other.size:
            return -1
        elif self.order_id > other.order_id:
            return 1
        elif self.order_id < other.order_id:
            return -1
        else:
            return 0

    def copy(self) -> LimitOrder:
        return LimitOrder(self.order_id, self.side, self.price, self.size)

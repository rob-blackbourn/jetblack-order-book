"""Order Book"""

from __future__ import annotations

from decimal import Decimal

from .order_types import Side


class LimitOrder:

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

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            self.price == other.price and
            self.size == other.size
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LimitOrder):
            raise ValueError("object must be a LimitOrder")
        if other.side > self.side:
            return True
        elif other.side < self.side:
            return False
        elif other.price > self.price:
            return True
        elif other.price < self.price:
            return False
        elif other.size > self.size:
            return True
        elif other.size < self.size:
            return False
        elif other.order_id > self.order_id:
            return True
        else:
            return False

    def copy(self) -> LimitOrder:
        return LimitOrder(self.order_id, self.side, self.price, self.size)

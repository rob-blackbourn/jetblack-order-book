"""Order Book"""

from __future__ import annotations

from decimal import Decimal


class Order:

    def __init__(self, price: Decimal, size: int, order_id: int) -> None:
        self.price = price
        self.size = size
        self.order_id = order_id

    def __repr__(self) -> str:
        return f"Order({self.price}, {self.size}, {self.order_id})"

    def __str__(self) -> str:
        return f"{self.price}x{self.size}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            self.price == other.price and
            self.size == other.size
        )

    def copy(self) -> Order:
        return Order(self.price, self.size, self.order_id)

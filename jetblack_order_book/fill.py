"""Order Book"""

from __future__ import annotations

from decimal import Decimal


class Fill:

    def __init__(
            self,
            buy_order_id: int,
            sell_order_id: int,
            price: Decimal,
            size: int
    ) -> None:
        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.price = price
        self.size = size

    def __repr__(self) -> str:
        return f"Fill({self.buy_order_id}, {self.sell_order_id}, {self.price}, {self.size})"

    def __str__(self) -> str:
        return f"{self.size}@{self.price}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Fill) and
            self.buy_order_id == other.buy_order_id and
            self.sell_order_id == other.sell_order_id and
            self.price == other.price and
            self.size == other.size
        )

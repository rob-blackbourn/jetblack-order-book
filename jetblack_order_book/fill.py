"""Fill"""

from decimal import Decimal
from typing import NamedTuple


class Fill(NamedTuple):
    """A fill is generated when a bid and an offer match or cross."""

    buy_order_id: int
    sell_order_id: int
    price: Decimal
    size: int

    def __str__(self) -> str:
        return f"{self.size}@{self.price}"

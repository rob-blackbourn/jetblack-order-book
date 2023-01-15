"""Fill"""

from decimal import Decimal
from typing import NamedTuple


class Fill(NamedTuple):
    buy_order_id: int
    sell_order_id: int
    price: Decimal
    size: int

    def __str__(self) -> str:
        return f"{self.size}@{self.price}"

"""Limit Order"""

from __future__ import annotations

from decimal import Decimal
from typing import NamedTuple, Optional

from .order_types import Side


class LimitOrder(NamedTuple):

    order_id: int
    side: Side
    price: Decimal
    size: int

    def __str__(self) -> str:
        return f"{self.price}x{self.size}"

    def copy(self) -> LimitOrder:
        return LimitOrder(self.order_id, self.side, self.price, self.size)

    def replace(
            self,
            order_id: Optional[int] = None,
            side: Optional[Side] = None,
            price: Optional[Decimal] = None,
            size: Optional[int] = None
    ) -> LimitOrder:
        return LimitOrder(
            self.order_id if order_id is None else order_id,
            self.side if side is None else side,
            self.price if price is None else price,
            self.size if size is None else size
        )

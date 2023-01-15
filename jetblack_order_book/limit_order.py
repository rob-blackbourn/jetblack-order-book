"""Limit Order"""

from __future__ import annotations

from decimal import Decimal
from typing import NamedTuple, Optional

from .order_types import Side


class LimitOrder:

    def __init__(
            self,
            order_id: int,
            side: Side,
            price: Decimal,
            size: int
    ) -> None:
        self._order_id = order_id
        self._side = side
        self._price = price
        self.size = size

    @property
    def order_id(self) -> int:
        return self._order_id

    @property
    def side(self) -> Side:
        return self._side

    @property
    def price(self) -> Decimal:
        return self._price

    def __str__(self) -> str:
        return f"{self.price}x{self.size}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, LimitOrder) and
            self.order_id == other.order_id and
            self.side == other.side and
            self.price == other.price and
            self.size == other.size

        )

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

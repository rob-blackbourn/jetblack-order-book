"""Order Book"""

from __future__ import annotations

from decimal import Decimal

from .linq import contains
from .limit_order import LimitOrder


class AggregateOrder:
    """A time priority aggregate order"""

    def __init__(self, order: LimitOrder) -> None:
        self._price = order.price
        self._orders = [order]

    @property
    def price(self) -> Decimal:
        return self._price

    @property
    def size(self) -> int:
        return sum(order.size for order in self._orders)

    def __repr__(self) -> str:
        return f"AggregateOrder({self._orders})"

    def __str__(self) -> str:
        return f"{self.price}x{self.size}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            self.price == other.price and
            self.size == other.size
        )

    def __bool__(self) -> bool:
        return len(self._orders) != 0

    def __iadd__(self, rhs: LimitOrder) -> AggregateOrder:
        assert isinstance(rhs, LimitOrder)
        self._orders.append(rhs)
        return self

    def __len__(self) -> int:
        return len(self._orders)

    def __getitem__(self, index: int) -> LimitOrder:
        return self._orders[index]

    def __delitem__(self, index: int) -> None:
        del self._orders[index]

    def __contains__(self, order_id: int) -> bool:
        return contains(self._orders, lambda x: x.order_id == order_id)

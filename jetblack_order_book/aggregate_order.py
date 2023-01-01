"""Order Book"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from .order import Order


class AggregateOrder:

    def __init__(self, orders: List[Order]) -> None:
        assert len(orders) > 0, "must be at least one order"
        self.price = orders[0].price
        assert all(
            self.price == order.price for order in orders[1:]
        ), "all orders must be the same price"
        self._orders = {
            order.order_id: order
            for order in orders
        }

    @classmethod
    def create(cls, price: Decimal, size: int, order_id: int = -1) -> AggregateOrder:
        return AggregateOrder([Order(price, size, order_id)])

    @property
    def size(self) -> int:
        return sum(order.size for order in self._orders.values())

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

    def __iadd__(self, rhs: Order) -> AggregateOrder:
        assert isinstance(rhs, Order)
        self._orders[rhs.order_id] = rhs
        return self

    def __len__(self) -> int:
        return len(self._orders)

    def __getitem__(self, order_id: int) -> Order:
        return self._orders[order_id]

    def __setitem__(self, order_id: int, order: Order) -> None:
        self._orders[order_id] = order

    def __delitem__(self, order_id: int) -> None:
        del self._orders[order_id]

    def __contains__(self, order_id: int) -> bool:
        return order_id in self._orders

    def copy(self) -> AggregateOrder:
        return AggregateOrder(
            [order.copy() for order in self._orders.values()]
        )

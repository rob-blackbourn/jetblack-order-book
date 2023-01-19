"""Aggregate Order"""

from __future__ import annotations

from collections import deque
from decimal import Decimal
from typing import List

from .utils import index_of
from .limit_order import LimitOrder, Style


class AggregateOrder:
    """A time priority aggregate order.

    All orders have the same price, but have different sizes, and are placed at
    different times.

    Orders at the beginning were placed before later orders, and should be
    executed first.
    """

    def __init__(self, order: LimitOrder) -> None:
        """Initialise an aggregate order with the first limit order.

        Args:
            order (LimitOrder): The limit order with which to start the
            aggregate order.
        """
        self._price = order.price
        self._orders = deque([order])

    @property
    def price(self) -> Decimal:
        """The price level of the aggregate order.

        Returns:
            Decimal: The price for the aggregate order.
        """
        return self._price

    @property
    def size(self) -> int:
        """The aggregate size of the order."""
        return sum(order.size for order in self._orders)

    @property
    def first(self) -> LimitOrder:
        """The first order to process."""
        return self._orders[0]

    @property
    def orders(self) -> List[LimitOrder]:
        return list(self._orders)

    def delete_first(self) -> None:
        """Delete the first order"""
        del self._orders[0]

    def append(self, order: LimitOrder) -> None:
        """Add a new order at the price level of this aggregate order.

        Args:
            order (LimitOrder): The new order.
        """
        assert order.price == self.price, "aggregate orders must be the same price"
        self._orders.append(order)

    def change_size(self, order_id: int, size: int) -> None:
        """Change the size of an order in the aggregate order.

        It is not possible to set the order size to zero (this would be a
        cancel).

        It is not possible to change the price or the side. Given that the
        algorithm is time weighted, allowing a change to the side or time would
        mean an order could be placed far from mid, then later adjusted, and
        with the benefit of time weighting, would be exercised first.

        Args:
            order_id (int): The order id.
            size (int): The new size.

        Raises:
            ValueError: When the size is less than or equal to zero.
            KeyError: When the order id is not in the aggregate order.
        """
        if size <= 0:
            raise ValueError("changes is size must be >= 0")
        index = index_of(self._orders, lambda x: x.order_id == order_id)
        if index == -1:
            raise KeyError("order not found")

        self._orders[index].size = size

    def cancel(self, order_id: int) -> None:
        """Cancel and order.

        Args:
            order_id (int): The order id.

        Raises:
            KeyError: If the order is not in the aggregate order.
        """
        index = index_of(self._orders, lambda x: x.order_id == order_id)
        if index == -1:
            raise KeyError("order not found")

        del self._orders[index]

    def find_by_style(self, style: Style) -> List[LimitOrder]:
        """Find orders by style.

        Args:
            style (Style): The style.

        Returns:
            List[LimitOrder]: The orders for the style.
        """
        return [
            order
            for order in self._orders
            if order.style == style
        ]

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            self.price == other.price and
            self.size == other.size
        )

    def __bool__(self) -> bool:
        """Check if there are any orders in the aggregate order.

        Returns:
            bool: Returns true if the aggregate order contains orders.
        """
        return len(self._orders) != 0

    def __len__(self) -> int:
        return len(self._orders)

    def __contains__(self, order_id: int) -> bool:
        return any(x.order_id == order_id for x in self._orders)

    def __repr__(self) -> str:
        return f"AggregateOrder({self._orders})"

    def __str__(self) -> str:
        return f"{self.price}x{self.size}"

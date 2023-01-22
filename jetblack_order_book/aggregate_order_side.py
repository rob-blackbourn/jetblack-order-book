"""Aggregate order side"""

from collections import deque
from itertools import islice
from typing import Deque, Sequence, Optional

from .aggregate_order import AggregateOrder
from .order import Order
from .utils import index_of


class AggregateOrderSide:
    """The aggregate orders for a side.

    This class handles side specific logic, in particular which orders are
    "best"; higher for bids, lower for offers.
    """

    def __init__(self, low_is_best: bool) -> None:
        """Initialise an aggregate order side.

        Args:
            side (Side): The side.
        """
        self._low_is_best = low_is_best
        self._orders: Deque[AggregateOrder] = deque()

    def depth(self, levels: Optional[int]) -> Sequence[AggregateOrder]:
        """Return the orders for the side.

        Args:
            levels (Optional[int]): The market depth to return.

        Returns:
            Sequence[AggregateOrder]: The orders.
        """
        if levels is None:
            return self._orders
        levels = min(levels, len(self._orders))
        if self._low_is_best:
            return tuple(islice(self._orders, 0, levels))
        else:
            return tuple(islice(
                self._orders,
                len(self._orders) - levels,
                len(self._orders)
            ))

    @property
    def best(self) -> AggregateOrder:
        """Get the order at the best price level."""
        return self._orders[0] if self._low_is_best else self._orders[-1]

    def delete_best(self) -> None:
        """Delete the order at the best price level."""
        if self._low_is_best:
            del self._orders[0]
        else:
            del self._orders[-1]

    def add_order(self, order: Order) -> None:
        """Add an order.

        Args:
            order (Order): The order.
        """
        # Find where the order should go.
        index = index_of(
            self._orders,
            lambda x: x.price >= order.price
        )
        if index == -1:
            # Add new highest price level.
            self._orders.append(AggregateOrder(order))
        elif self._orders[index].price == order.price:
            # Add the order to an existing price level. Adding to the end
            # means newer orders are executed first (time weighted).
            self._orders[index].append(order)
        else:
            # Insert a new lowest price level
            self._orders.insert(index, AggregateOrder(order))

    def amend_order(self, order: Order, size: int) -> None:
        """Amend an order.

        Args:
            order (Order): The order.
            size (int): The new size.

        Raises:
            ValueError: If there are no orders at the price.
        """
        # Find the position of the order in the aggregate orders.
        index = index_of(
            self._orders,
            lambda x: x.price == order.price
        )
        if index == -1:
            raise ValueError("no order at this price")

        # Change the size.
        self._orders[index].change_size(order.order_id, size)

    def cancel_order(self, order: Order) -> None:
        """Cancel an order.

        Args:
            order (Order): The order

        Raises:
            KeyError: If the order is not in this side.
        """
        index = index_of(
            self._orders,
            lambda x: x.price == order.price
        )
        if index == -1:
            raise KeyError("The aggregate order could not be found")

        aggregate_order = self._orders[index]
        aggregate_order.cancel(order.order_id)
        if len(aggregate_order) == 0:
            # If there are no orders left at this price level, delete the
            # aggregate order.
            del self._orders[index]

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, AggregateOrderSide) and
            self._orders == other._orders
        )

    def __bool__(self) -> bool:
        """A side is True if it has orders; otherwise False."""
        return bool(self._orders)

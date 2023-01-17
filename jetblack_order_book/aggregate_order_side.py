"""Aggregate order side"""

from collections import deque
from itertools import islice
from typing import Deque, Sequence, Optional

from .aggregate_order import AggregateOrder
from .limit_order import LimitOrder
from .linq import index_of
from .order_types import Side


class AggregateOrderSide:
    """The aggregate orders for a side"""

    def __init__(self, side: Side) -> None:
        self.side = side
        self._orders: Deque[AggregateOrder] = deque()

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            all(a == b for a, b in zip(self._orders, other._orders))
        )

    def __bool__(self) -> bool:
        return bool(self._orders)

    def orders(self, levels: Optional[int]) -> Sequence[AggregateOrder]:
        if levels is None:
            return self._orders
        levels = min(levels, len(self._orders))
        if self.side == Side.BUY:
            return tuple(islice(
                self._orders,
                len(self._orders) - levels,
                len(self._orders)
            ))
        else:
            return tuple(islice(self._orders, 0, levels))

    @property
    def best(self) -> AggregateOrder:
        return self._orders[-1] if self.side == Side.BUY else self._orders[0]

    def delete_best(self) -> None:
        if self.side == Side.BUY:
            del self._orders[-1]
        else:
            del self._orders[0]

    def add_limit_order(self, order: LimitOrder):
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

    def amend_limit_order(self, order: LimitOrder, size: int) -> None:
        # Find the position of the order in the aggregate orders.
        index = index_of(
            self._orders,
            lambda x: x.price == order.price
        )
        if index == -1:
            raise ValueError("no order at this price")

        # Change the size.
        self._orders[index].change_size(order.order_id, size)

    def cancel_limit_order(self, order: LimitOrder) -> None:
        pass
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

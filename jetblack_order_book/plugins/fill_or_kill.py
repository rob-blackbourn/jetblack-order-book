"""A plugin for fill-or-kill orders.

A fill-or-kill order must be completely filled; otherwise it must be cancelled.

The pre_fill hook can be used to catch fill-or-kill orders that cannot be
completely filled.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from ..abstract_types import (
    AbstractOrderBookManager,
    Plugin
)
from ..aggregate_order import AggregateOrder
from ..aggregate_order_side import AggregateOrderSide
from ..order import Order, Style


class FillOrKillPlugin(Plugin):
    """A plugin which handles fill mor kill orders"""

    @property
    def valid_styles(self) -> Sequence[Style]:
        return (Style.FILL_OR_KILL,)

    def pre_fill(
            self,
            manager: AbstractOrderBookManager,
            bids: AggregateOrderSide,
            offers: AggregateOrderSide,
            aggressor: Order
    ) -> List[Order]:

        cancels: List[Order] = []

        # Ensure time weighted.
        order = (
            self._handle_fill_or_kill(
                bids.best,
                offers.best
            )
            if bids.best.first.order_id < offers.best.first.order_id
            else self._handle_fill_or_kill(
                offers.best,
                bids.best
            )
        )

        if order is not None:
            cancels.append(order)

        return cancels

    @classmethod
    def _handle_fill_or_kill(
            cls,
            order1: AggregateOrder,
            order2: AggregateOrder,
    ) -> Optional[Order]:
        if cls._should_cancel(order1.first, order2.first):
            return order1.first

        if cls._should_cancel(order2.first, order1.first):
            return order2.first

        return None

    @classmethod
    def _should_cancel(cls, order1: Order, order2: Order) -> bool:
        # If this is a fill-or-kill order the order must be completely filled.
        return (
            order1.style == Style.FILL_OR_KILL and
            order1.size > order2.size
        )

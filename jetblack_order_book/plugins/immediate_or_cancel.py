"""A plugin for immediate-or-cancel orders.

An immediate-or-cancel (IOC) order is an order to buy or sell that must be
executed immediately. Any portion of an IOC order that cannot be filled
immediately will be cancelled.

The implications for the implementation is that IOC orders can be pruned on
insertion. An IOC order at a worse price level should simply be rejected. This
can be handled with the pre_create hook. If a new IOC order was added at a
better price, IOC orders at the lower price can never be hit immediately and
should be cancelled. This can be handled with the post_create hook.

Finally all IOC orders that were at the best price level during a match that
were not executed must be cancelled. This can be handled by the post_match hook.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Sequence

from ..abstract_types import (
    AbstractOrderBookManager,
    Plugin
)
from ..aggregate_order import AggregateOrder
from ..order import Order, Side, Style


class ImmediateOrCancelPlugin(Plugin):
    """A plugin which handles fill mor kill orders"""

    @property
    def valid_styles(self) -> Sequence[Style]:
        return (Style.IMMEDIATE_OR_CANCEL,)

    def __init__(self) -> None:
        self._immediate_or_cancel: Dict[Side, AggregateOrder] = {}

    def pre_create(
            self,
            manager: AbstractOrderBookManager,
            side: Side,
            price: Decimal,
            style: Style
    ) -> bool:
        if style != Style.IMMEDIATE_OR_CANCEL:
            return True

        # If there are immediate and cancel orders at a better price then this
        # order is invalid.

        if side not in self._immediate_or_cancel:
            # There are no immediate-or-cancel orders for this side, so the
            # order is valid.
            return True
        if side == Side.BUY and price >= self._immediate_or_cancel[side].price:
            # The order has the same or a greater price than the exiting buy
            # immediate-or-cancel orders, so the order is valid.
            return True
        if side == Side.SELL and price <= self._immediate_or_cancel[side].price:
            # The order has the same or a lesser price than the exiting sell
            # immediate-or-cancel orders, so the order is valid.
            return True

        # The order should be rejected.
        return False

    def post_create(
            self,
            manager: AbstractOrderBookManager,
            order: Order
    ) -> List[Order]:
        # If this order is at a better price level than existing immediate or
        # cancel orders, they should be cancelled.

        if order.style != Style.IMMEDIATE_OR_CANCEL:
            # Only immediate-or-cancel orders are relevant.
            return []

        if order.side not in self._immediate_or_cancel:
            # If there are no immediate-or-cancel orders for this side just
            # add it.
            self._immediate_or_cancel[order.side] = AggregateOrder(order)
            return []

        if order.price == self._immediate_or_cancel[order.side].price:
            # If this order is at the same price append it.
            self._immediate_or_cancel[order.side].append(order)
            return []

        # As the pre_create function has already established this order is valid
        # there must be other immediate-or-cancel orders at a worse price. Those
        # orders must be cancelled, replaced with the new order.
        cancels = self._immediate_or_cancel[order.side].orders
        self._immediate_or_cancel[order.side] = AggregateOrder(order)

        return cancels

    def post_delete(
            self,
            manager: AbstractOrderBookManager,
            order: Order
    ) -> None:
        # Remove the order from the local cache.
        if (
                order.side in self._immediate_or_cancel and
                order.order_id in self._immediate_or_cancel[order.side]
        ):
            self._immediate_or_cancel[order.side].cancel(order.order_id)

    def post_match(
            self,
            manager: AbstractOrderBookManager,
    ) -> List[Order]:
        # After a match any immediate-or-cancel orders at the best price level
        # must be cancelled.

        cancels: List[Order] = []

        if manager.bids:
            orders = manager.bids.best.find_all(
                lambda x: x.style == Style.IMMEDIATE_OR_CANCEL
            )
            cancels += orders

        if manager.offers:
            orders = manager.offers.best.find_all(
                lambda x: x.style == Style.IMMEDIATE_OR_CANCEL
            )
            cancels += orders

        return cancels

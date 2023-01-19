"""Immediate or cancel plugin"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Sequence

from ..abstract_types import (
    AbstractOrderBookManager,
    AbstractOrderBookManagerPlugin
)
from ..aggregate_order import AggregateOrder
from ..limit_order import LimitOrder, Side, Style


class ImmediateOrCancelPlugin(AbstractOrderBookManagerPlugin):
    """A plugin which handles fill mor kill orders"""

    @property
    def valid_styles(self) -> Sequence[Style]:
        return (Style.IMMEDIATE_OR_CANCEL,)

    def __init__(self, manager: AbstractOrderBookManager) -> None:
        super().__init__(manager)
        self._immediate_or_cancel: Dict[Side, AggregateOrder] = {}

    def post_create(self, order: LimitOrder) -> List[int]:
        if order.style != Style.IMMEDIATE_OR_CANCEL:
            return []

        if order.side not in self._immediate_or_cancel:
            self._immediate_or_cancel[order.side] = AggregateOrder(order)
            return []

        if order.price == self._immediate_or_cancel[order.side].price:
            self._immediate_or_cancel[order.side].append(order)
            return []

        cancels: List[int] = list(map(
            lambda x: x.order_id,
            self._immediate_or_cancel[order.side].orders
        ))
        for order_id in cancels:
            self.manager.cancel_limit_order(order_id)
        self._immediate_or_cancel[order.side] = AggregateOrder(order)

        return cancels

    def post_delete(self, order: LimitOrder) -> None:
        if (
                order.side in self._immediate_or_cancel and
                order.order_id in self._immediate_or_cancel[order.side]
        ):
            self._immediate_or_cancel[order.side].cancel(order.order_id)

    def pre_create(self, side: Side, price: Decimal, style: Style) -> bool:
        if style != Style.IMMEDIATE_OR_CANCEL:
            return True

        if side not in self._immediate_or_cancel:
            return True
        if side == Side.BUY and price >= self._immediate_or_cancel[side].price:
            return True
        if side == Side.SELL and price <= self._immediate_or_cancel[side].price:
            return True
        return False

    def post_match(self) -> List[LimitOrder]:
        cancels: List[LimitOrder] = []

        if self.manager.bids:
            orders = self.manager.bids.best.find_by_style(
                Style.IMMEDIATE_OR_CANCEL
            )
            cancels += orders

        if self.manager.offers:
            orders = self.manager.offers.best.find_by_style(
                Style.IMMEDIATE_OR_CANCEL
            )
            cancels += orders

        return cancels


def create_immediate_or_cancel_plugin(
        manager: AbstractOrderBookManager
) -> AbstractOrderBookManagerPlugin:
    """Create a plugin for `Style.IMMEDIATE_OR_CANCEL` orders.

    Args:
        manager (AbstractOrderBookManager): The order book manager.

    Returns:
        AbstractOrderBookManagerPlugin: A plugin for immediate or cancel orders.
    """
    return ImmediateOrCancelPlugin(manager)

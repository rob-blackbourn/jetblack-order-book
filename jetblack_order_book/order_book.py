"""Order Book"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional, Sequence, Tuple

from .abstract_types import AbstractOrderBook
from .aggregate_order import AggregateOrder
from .aggregate_order_side import AggregateOrderSide
from .fill import Fill
from .limit_order import Side, Style
from .order_book_manager import OrderBookManager
from .plugins import (
    create_fill_or_kill_plugin,
    create_immediate_or_cancel_plugin
)


class OrderBook(AbstractOrderBook):
    """An order book"""

    def __init__(self) -> None:
        self._manager = OrderBookManager(
            (create_fill_or_kill_plugin, create_immediate_or_cancel_plugin)
        )

    @property
    def bids(self) -> AggregateOrderSide:
        return self._manager.bids

    @property
    def offers(self) -> AggregateOrderSide:
        return self._manager.offers

    def book_depth(
            self,
            levels: Optional[int]
    ) -> Tuple[Sequence[AggregateOrder], Sequence[AggregateOrder]]:
        return self._manager.book_depth(levels)

    def add_limit_order(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[int], List[Fill], List[int]]:
        return self._manager.add_limit_order(side, price, size, style)

    def amend_limit_order(self, order_id: int, size: int) -> None:
        self._manager.amend_limit_order(order_id, size)

    def cancel_limit_order(self, order_id: int) -> None:
        self._manager.cancel_limit_order(order_id)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, OrderBook) and
            self._manager == other._manager
        )

    def __repr__(self) -> str:
        return repr(self._manager)

    def __str__(self) -> str:
        return str(self._manager)

    def __format__(self, format_spec: str) -> str:
        return format(self._manager, format_spec)

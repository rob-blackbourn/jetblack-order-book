"""Order Book"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional, Sequence, Tuple

from .abstract_types import AbstractOrderBook, PluginFactory
from .aggregate_order import AggregateOrder
from .aggregate_order_side import AggregateOrderSide
from .constants import ALL_PLUGINS
from .fill import Fill
from .order import Side, Style
from .order_book_manager import OrderBookManager


class OrderBook(AbstractOrderBook):
    """An order book

    This is a wrapper around OrderBookManager, to present a clean interface to
    the client.
    """

    def __init__(
            self,
            plugins: Sequence[PluginFactory] = ALL_PLUGINS
    ) -> None:
        """Initialise the order book.

        Args:
            plugins (Sequence[PluginFactory], optional): Plugins to use to
                handle order styles. Defaults to `ALL_PLUGINS`.
        """
        self._manager = OrderBookManager(plugins)

    @property
    def limit_bids(self) -> AggregateOrderSide:
        return self._manager.limit_bids

    @property
    def limit_offers(self) -> AggregateOrderSide:
        return self._manager.limit_offers

    @property
    def stop_bids(self) -> AggregateOrderSide:
        return self._manager.stop_bids

    @property
    def stop_offers(self) -> AggregateOrderSide:
        return self._manager.stop_offers

    def book_depth(
            self,
            levels: Optional[int]
    ) -> Tuple[Sequence[AggregateOrder], Sequence[AggregateOrder]]:
        return self._manager.book_depth(levels)

    def add_order(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[int], List[Fill], List[int]]:
        return self._manager.add_order(side, price, size, style)

    def amend_order(self, order_id: int, size: int) -> None:
        self._manager.amend_order(order_id, size)

    def cancel_order(self, order_id: int) -> None:
        self._manager.cancel_order(order_id)

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

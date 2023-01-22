"""A plugin for book-or-cancel orders.

A book-or-cancel order must enter the book before being filled; otherwise it
must be cancelled.

The pre_fill hook can be used to check that the order will not be immediately
filled.
"""

from __future__ import annotations

from typing import List, Sequence

from ..abstract_types import (
    AbstractOrderBookManager,
    AbstractOrderBookManagerPlugin
)
from ..aggregate_order_side import AggregateOrderSide
from ..order import Order, Style


class BookOrCancelPlugin(AbstractOrderBookManagerPlugin):
    """A plugin which handles fill mor kill orders"""

    @property
    def valid_styles(self) -> Sequence[Style]:
        return (Style.BOOK_OR_CANCEL,)

    def pre_fill(
            self,
            bids: AggregateOrderSide,
            offers: AggregateOrderSide,
            aggressor: Order
    ) -> List[Order]:

        cancels: List[Order] = []

        if (
                bids.best.first.style == Style.BOOK_OR_CANCEL and
                aggressor.order_id == bids.best.first.order_id
        ):
            cancels.append(bids.best.first)
        elif (
                offers.best.first.style == Style.BOOK_OR_CANCEL and
                aggressor.order_id == offers.best.first.order_id
        ):
            cancels.append(offers.best.first)

        return cancels


def create_book_or_cancel_plugin(
        manager: AbstractOrderBookManager
) -> AbstractOrderBookManagerPlugin:
    """Create a plugin for `Style.BOOK_OR_CANCEL` orders.

    Args:
        manager (AbstractOrderBookManager): The order book manager.

    Returns:
        AbstractOrderBookManagerPlugin: The book-or-cancel plugin.
    """
    return BookOrCancelPlugin(manager)

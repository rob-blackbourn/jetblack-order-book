"""Fill or kill plugin"""

from __future__ import annotations

from typing import List, Sequence

from ..abstract_types import (
    AbstractOrderBookManager,
    AbstractOrderBookManagerPlugin
)
from ..limit_order import LimitOrder, Style


class BookOrCancelPlugin(AbstractOrderBookManagerPlugin):
    """A plugin which handles fill mor kill orders"""

    @property
    def valid_styles(self) -> Sequence[Style]:
        return (Style.BOOK_OR_CANCEL,)

    def pre_fill(self, aggressor: LimitOrder) -> List[LimitOrder]:

        cancels: List[LimitOrder] = []

        if (
                self.manager.bids.best.first.style == Style.BOOK_OR_CANCEL and
                aggressor.order_id == self.manager.bids.best.first.order_id
        ):
            cancels.append(self.manager.bids.best.first)
        elif (
                self.manager.offers.best.first.style == Style.BOOK_OR_CANCEL and
                aggressor.order_id == self.manager.offers.best.first.order_id
        ):
            cancels.append(self.manager.offers.best.first)

        return cancels


def create_book_or_cancel_plugin(
        manager: AbstractOrderBookManager
) -> AbstractOrderBookManagerPlugin:
    """Create a plugin for `Style.BOOK_OR_CANCEL` orders.

    Args:
        manager (AbstractOrderBookManager): The order book manager.

    Returns:
        AbstractOrderBookManagerPlugin: The fill or kill plugin.
    """
    return BookOrCancelPlugin(manager)

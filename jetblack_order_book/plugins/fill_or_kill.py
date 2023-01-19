"""Fill or kill plugin"""

from __future__ import annotations

from typing import List, Optional, Sequence

from ..abstract_types import (
    AbstractOrderBookManager,
    AbstractOrderBookManagerPlugin
)
from ..aggregate_order import AggregateOrder
from ..limit_order import LimitOrder, Style


class FillOrKillPlugin(AbstractOrderBookManagerPlugin):
    """A plugin which handles fill mor kill orders"""

    @property
    def valid_styles(self) -> Sequence[Style]:
        return (Style.FILL_OR_KILL,)

    def pre_fill(self) -> List[LimitOrder]:

        cancels: List[LimitOrder] = []
        order = self._handle_fill_or_kill(
            self.manager.bids.best,
            self.manager.offers.best
        )
        if order is not None:
            cancels.append(order)

        return cancels

    def _handle_fill_or_kill(
            self,
            bids: AggregateOrder,
            offers: AggregateOrder,
    ) -> Optional[LimitOrder]:
        if bids.first.order_id > offers.first.order_id:
            # Ensure time weighted treatment.
            return self._handle_fill_or_kill(offers, bids)  # pylint: disable=arguments-out-of-order

        if (
            bids.first.style == Style.FILL_OR_KILL and
            bids.first.size > offers.first.size
        ):
            return bids.first

        if (
            offers.first.style == Style.FILL_OR_KILL and
            offers.first.size > bids.first.size
        ):
            return offers.first

        return None


def create_fill_or_kill_plugin(
        manager: AbstractOrderBookManager
) -> AbstractOrderBookManagerPlugin:
    """Create a plugin for `Style.FILL_OR_KILL` orders.

    Args:
        manager (AbstractOrderBookManager): The order book manager.

    Returns:
        AbstractOrderBookManagerPlugin: The fill or kill plugin.
    """
    return FillOrKillPlugin(manager)

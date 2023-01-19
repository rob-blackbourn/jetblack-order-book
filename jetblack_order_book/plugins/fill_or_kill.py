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

        # Ensure time weighted.
        order = (
            self._handle_fill_or_kill(
                self.manager.bids.best,
                self.manager.offers.best
            )
            if self.manager.bids.best.first.order_id < self.manager.offers.best.first.order_id
            else self._handle_fill_or_kill(
                self.manager.offers.best,
                self.manager.bids.best
            )
        )

        if order is not None:
            cancels.append(order)

        return cancels

    def _handle_fill_or_kill(
            self,
            order1: AggregateOrder,
            order2: AggregateOrder,
    ) -> Optional[LimitOrder]:
        if (
            order1.first.style == Style.FILL_OR_KILL and
            order1.first.size > order2.first.size
        ):
            return order1.first

        if (
            order2.first.style == Style.FILL_OR_KILL and
            order2.first.size > order1.first.size
        ):
            return order2.first

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

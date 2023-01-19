"""Fill or kill plugin"""

from __future__ import annotations

from typing import List, Sequence

from ..abstract_types import (
    AbstractOrderBookManager,
    AbstractOrderBookManagerPlugin
)
from ..limit_order import LimitOrder, Style


class FillOrKillPlugin(AbstractOrderBookManagerPlugin):
    """A plugin which handles fill mor kill orders"""

    @property
    def valid_styles(self) -> Sequence[Style]:
        return (Style.FILL_OR_KILL,)

    def pre_fill(self) -> List[LimitOrder]:
        cancels: List[LimitOrder] = []
        order = self.manager.bids.best.handle_fill_or_kill(
            self.manager.offers.best
        )
        if order is not None:
            cancels.append(order)

        return cancels


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

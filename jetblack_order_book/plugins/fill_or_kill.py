"""Fill or kill plugin"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from ..abstract_types import AbstractOrderBookManagerPlugin
from ..limit_order import LimitOrder, Side, Style


class FillOrKillPlugin(AbstractOrderBookManagerPlugin):
    """A plugin which handles fill mor kill orders"""

    def post_create(self, order: LimitOrder) -> List[int]:
        return []

    def post_delete(self, order: LimitOrder) -> None:
        return

    def is_valid(self, side: Side, price: Decimal, style: Style) -> bool:
        return True

    def find_cancellable_orders(self, order: LimitOrder) -> List[int]:
        return []

    def pre_fill_check(self) -> List[LimitOrder]:
        cancels: List[LimitOrder] = []
        order = self.manager.bids.best.handle_fill_or_kill(
            self.manager.offers.best
        )
        if order is not None:
            cancels.append(order)

        return cancels

    def post_match_check(self) -> List[LimitOrder]:
        return []

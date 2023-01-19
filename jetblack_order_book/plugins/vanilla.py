"""Fill or kill plugin"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Sequence

from ..abstract_types import AbstractOrderBookManagerPlugin
from ..limit_order import LimitOrder, Side, Style


class VanillaPlugin(AbstractOrderBookManagerPlugin):
    """A plugin which handles fill mor kill orders"""

    @property
    def valid_styles(self) -> Sequence[Style]:
        return (Style.VANILLA,)

    def post_create(self, order: LimitOrder) -> List[int]:
        return []

    def post_delete(self, order: LimitOrder) -> None:
        return

    def is_valid(self, side: Side, price: Decimal, style: Style) -> bool:
        return True

    def find_cancellable_orders(self, order: LimitOrder) -> List[int]:
        return []

    def pre_fill_check(self) -> List[LimitOrder]:
        return []

    def post_match_check(self) -> List[LimitOrder]:
        return []

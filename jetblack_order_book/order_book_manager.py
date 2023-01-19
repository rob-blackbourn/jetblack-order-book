"""Order Book Manager"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional, Sequence, Tuple, Type

from .abstract_types import (
    AbstractOrderBookManager,
    AbstractOrderBookManagerPlugin
)
from .aggregate_order import AggregateOrder
from .aggregate_order_side import AggregateOrderSide
from .fill import Fill
from .limit_order import LimitOrder, Side, Style


class OrderBookManager(AbstractOrderBookManager):
    """An order book manager"""

    def __init__(
            self, plugins: Sequence[Type[AbstractOrderBookManagerPlugin]]
    ) -> None:
        self._plugins = [
            plugin(self) for plugin in plugins
        ]

        self._supported_styles = set(
            style
            for plugin in self._plugins
            for style in plugin.valid_styles
        )
        self._supported_styles.add(Style.VANILLA)

        self._orders: Dict[int, LimitOrder] = {}
        self._next_order_id = 1
        self._sides = {
            Side.BUY: AggregateOrderSide(Side.BUY),
            Side.SELL: AggregateOrderSide(Side.SELL)
        }

    def side(self, side: Side) -> AggregateOrderSide:
        return self._sides[side]

    @property
    def bids(self) -> AggregateOrderSide:
        return self.side(Side.BUY)

    @property
    def offers(self) -> AggregateOrderSide:
        return self.side(Side.SELL)

    def book_depth(
            self,
            levels: Optional[int]
    ) -> Tuple[Sequence[AggregateOrder], Sequence[AggregateOrder]]:
        return self.bids.orders(levels), self.offers.orders(levels)

    def add_limit_order(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[int], List[Fill], List[int]]:
        if style not in self._supported_styles:
            raise ValueError('unsupported style')

        order, cancels = self.create(
            side,
            price,
            size,
            style
        )

        if order is None:
            return None, [], []

        self.side(order.side).add_limit_order(order)

        # Return the order id and any fills that were generated. The id of the
        # order that instigated the changes is supplied.
        return order.order_id, *self._match(order.order_id, cancels)

    def amend_limit_order(self, order_id: int, size: int) -> None:
        assert size > 0, "size must be greater than 0"

        order = self.find(order_id)
        self.side(order.side).amend_limit_order(order, size)

    def cancel_limit_order(self, order_id: int) -> None:
        order = self.find(order_id)
        self.side(order.side).cancel_limit_order(order)
        self.delete(order)

    def create(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[LimitOrder], List[int]]:
        if not self._is_valid(side, price, style):
            return None, []

        order = LimitOrder(self._next_order_id, side, price, size, style)
        self._orders[order.order_id] = order
        self._next_order_id += 1

        cancels = self._post_create(order)

        return order, cancels

    def _post_create(self, order: LimitOrder) -> List[int]:
        cancels: List[int] = []

        for plugin in self._plugins:
            cancels += plugin.post_create(order)

        return cancels

    def find(self, order_id: int) -> LimitOrder:
        return self._orders[order_id]

    def delete(self, order: LimitOrder) -> None:
        del self._orders[order.order_id]
        self._post_delete(order)

    def _post_delete(self, order: LimitOrder) -> None:
        for plugin in self._plugins:
            plugin.post_delete(order)

    def _is_valid(self, side: Side, price: Decimal, style: Style) -> bool:
        for plugin in self._plugins:
            if not plugin.is_valid(side, price, style):
                return False

        return True

    def _find_cancellable_orders(self, order: LimitOrder) -> List[int]:
        cancel_orders: List[int] = []

        for plugin in self._plugins:
            cancel_orders += plugin.find_cancellable_orders(order)

        return cancel_orders

    def _match(
            self,
            aggressor_order_id: int,
            cancels: List[int]
    ) -> Tuple[List[Fill], List[int]]:
        """Match bids against offers generating fills.

        Args:
            aggressor_order_id (int): The order id that generated the match.
            cancels (List[int]): A list of already cancelled orders.

        Returns:
            Tuple[List[Fill], List[int]: The fills and cancels.
        """
        fills: List[Fill] = []
        while (
                self.bids and
                self.offers and
                self.bids.best.price >= self.offers.best.price
        ):
            while self.bids.best and self.offers.best:

                # Check if any orders require cancellation.
                cancel_orders = self._pre_fill_check()
                if cancel_orders:
                    for order in cancel_orders:
                        cancels.append(order.order_id)
                        self.side(order.side).cancel_limit_order(order)
                    break

                # The price is that of the newest order in case of a cross;
                # where the newest order price exceeds (rather than matched)
                # the best opposing price.
                fill_size = min(
                    self.bids.best.first.size,
                    self.offers.best.first.size
                )
                fill_price = (
                    self.bids.best.first.price
                    if self.bids.best.first.order_id == aggressor_order_id
                    else self.offers.best.first.price
                )

                fills.append(
                    Fill(
                        self.bids.best.first.order_id,
                        self.offers.best.first.order_id,
                        fill_price,
                        fill_size)
                )

                # Decrement the orders by the trade size, then check if the
                # orders have been completely executed.

                self.bids.best.first.size -= fill_size
                if self.bids.best.first.size == 0:
                    self.delete(self.bids.best.first)
                    self.bids.best.delete_first()

                self.offers.best.first.size -= fill_size
                if self.offers.best.first.size == 0:
                    self.delete(self.offers.best.first)
                    self.offers.best.delete_first()

            # Check if any orders require cancellation.
            cancel_orders = self._post_match_check()
            for order in cancel_orders:
                cancels.append(order.order_id)
                self.side(order.side).cancel_limit_order(order)

            # if all orders have been executed at this price level remove the
            # price level.
            if self.bids and not self.bids.best:
                self.bids.delete_best()
            if self.offers and not self.offers.best:
                self.offers.delete_best()

        return fills, cancels

    def _pre_fill_check(self) -> List[LimitOrder]:
        cancels: List[LimitOrder] = []

        for plugin in self._plugins:
            cancels += plugin.pre_fill_check()

        return cancels

    def _post_match_check(self) -> List[LimitOrder]:
        cancels: List[LimitOrder] = []

        for plugin in self._plugins:
            cancels += plugin.post_match_check()

        return cancels

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            self.bids == other.bids and
            self.offers == other.offers
        )

    def __repr__(self) -> str:
        return f"OrderBook({self.bids}, {self.offers})"

    def __str__(self) -> str:
        return format(self, "")

    def __format__(self, format_spec: str) -> str:
        levels = None if not format_spec else int(format_spec)
        assert levels is None or levels > 0, 'levels should be > 0'
        bids, offers = self.book_depth(levels)
        return f'{",".join(map(str, bids))} : {",".join(map(str, offers))}'

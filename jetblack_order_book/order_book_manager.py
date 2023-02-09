"""Order Book Manager"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional, Sequence, Tuple

from .abstract_types import (
    AbstractOrderBookManager,
    PluginFactory
)
from .aggregate_order import AggregateOrder
from .aggregate_order_side import AggregateOrderSide
from .fill import Fill
from .order import Order, Side, Style


class OrderBookManager(AbstractOrderBookManager):
    """An order book manager"""

    def __init__(self, plugins: Sequence[PluginFactory]) -> None:
        """Initialise the order book manager.

        Args:
            plugins (Sequence[PluginFactory]): Plugins used to managed order
                styles.
        """
        self._plugins = [
            plugin(self) for plugin in plugins
        ]

        self._supported_styles = set(
            style
            for plugin in self._plugins
            for style in plugin.valid_styles
        )
        self._supported_styles.add(Style.LIMIT)
        self._supported_styles.add(Style.STOP)

        self._orders: Dict[int, Order] = {}
        self._next_order_id = 1
        self._limit_sides = {
            Side.BUY: AggregateOrderSide(False),
            Side.SELL: AggregateOrderSide(True)
        }
        self._stop_sides = {
            Side.BUY: AggregateOrderSide(True),
            Side.SELL: AggregateOrderSide(False)
        }

    def _side(self, order: Order) -> AggregateOrderSide:
        return (
            self._limit_sides[order.side] if order.style != Style.STOP
            else self._stop_sides[order.side]
        )

    @property
    def bids(self) -> AggregateOrderSide:
        return self._limit_sides[Side.BUY]

    @property
    def offers(self) -> AggregateOrderSide:
        return self._limit_sides[Side.SELL]

    @property
    def stop_bids(self) -> AggregateOrderSide:
        return self._stop_sides[Side.BUY]

    @property
    def stop_offers(self) -> AggregateOrderSide:
        return self._stop_sides[Side.SELL]

    def book_depth(
            self,
            levels: Optional[int]
    ) -> Tuple[Sequence[AggregateOrder], Sequence[AggregateOrder]]:
        return self.bids.depth(levels), self.offers.depth(levels)

    def add_order(
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

        self._side(order).add_order(order)

        # Try to match the new order with the book. The id of the order that
        # instigated the changes is supplied. The match may generated fills and
        # cancellations.
        fills, cancels = self._match(order, cancels)

        # Return the order id and any fills and cancels that were generated.
        return order.order_id, fills, list(map(lambda x: x.order_id, cancels))

    def amend_order(self, order_id: int, size: int) -> None:
        if size <= 0:
            raise ValueError("size must be greater than 0")

        order = self.find(order_id)
        self._side(order).amend_order(order, size)

    def cancel_order(self, order_id: int) -> None:
        order = self.find(order_id)
        self._side(order).cancel_order(order)
        self.delete(order)

    def create(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[Order], List[Order]]:
        if not self._pre_create(side, price, style):
            return None, []

        order = Order(self._next_order_id, side, price, size, style)
        self._orders[order.order_id] = order
        self._next_order_id += 1

        cancels = self._post_create(order)
        for cancel in cancels:
            self.cancel_order(cancel.order_id)

        return order, cancels

    def _pre_create(self, side: Side, price: Decimal, style: Style) -> bool:
        for plugin in self._plugins:
            if not plugin.pre_create(side, price, style):
                return False

        return True

    def _post_create(self, order: Order) -> List[Order]:
        cancels: List[Order] = []

        for plugin in self._plugins:
            cancels += plugin.post_create(order)

        return cancels

    def find(self, order_id: int) -> Order:
        return self._orders[order_id]

    def delete(self, order: Order) -> None:
        del self._orders[order.order_id]
        self._post_delete(order)

    def _post_delete(self, order: Order) -> None:
        for plugin in self._plugins:
            plugin.post_delete(order)

    def _match(
            self,
            aggressor: Order,
            cancels: List[Order]
    ) -> Tuple[List[Fill], List[Order]]:
        """Match bids against offers generating fills.

        Args:
            aggressor (Order): The order that instigated the match.
            cancels (List[Order]): A list of already cancelled orders.

        Returns:
            Tuple[List[Order], List[Order]: The fills and cancels.
        """
        fills: List[Fill] = []
        while self._can_match():
            bids, offers = self._fillable_sides(aggressor)

            while bids.best and offers.best:

                # Check if any orders require cancellation.
                cancel_orders = self._pre_fill(bids, offers, aggressor)
                if cancel_orders:
                    for order in cancel_orders:
                        cancels.append(order)
                        self._side(order).cancel_order(order)
                    break

                fills.append(
                    self._fill_best(bids, offers, aggressor)
                )

            # Check if any orders require cancellation.
            cancel_orders = self._post_match()
            for order in cancel_orders:
                cancels.append(order)
                self._side(order).cancel_order(order)

            # if all orders have been executed at this price level remove the
            # price level.
            if self.bids and not self.bids.best:
                self.bids.delete_best()
            if self.offers and not self.offers.best:
                self.offers.delete_best()

        return fills, cancels

    def _can_match(self) -> bool:
        if (
                self.bids and
                self.offers and
                self.bids.best.price >= self.offers.best.price
        ):
            return True

        # Sell stop
        # The buy price drops to at or below the sell stop
        if (
            self.bids and
            self.stop_offers and
            self.bids.best.price <= self.stop_offers.best.price
        ):
            return True

        return False

    def _fill_best(
            self,
            bids: AggregateOrderSide,
            offers: AggregateOrderSide,
            aggressor: Order
    ) -> Fill:
        # The price is that of the newest order in case of a cross;
        # where the newest order price exceeds (rather than matched)
        # the best opposing price.
        fill_size = min(
            bids.best.first.size,
            offers.best.first.size
        )
        fill_price = (
            bids.best.first.price
            if bids.best.first.order_id == aggressor.order_id
            else offers.best.first.price
        )

        fill = Fill(
            bids.best.first.order_id,
            offers.best.first.order_id,
            fill_price,
            fill_size
        )

        # Decrement the orders by the trade size, then check if the
        # orders have been completely executed; if they have, delete
        # them.

        bids.best.first.size -= fill_size
        if bids.best.first.size == 0:
            self.delete(bids.best.first)
            bids.best.delete_first()

        offers.best.first.size -= fill_size
        if offers.best.first.size == 0:
            self.delete(offers.best.first)
            offers.best.delete_first()

        return fill

    def _fillable_sides(self, aggressor: Order) -> Tuple[AggregateOrderSide, AggregateOrderSide]:
        if (
            aggressor.side == Side.SELL and
            self.stop_bids and
            self.stop_bids.best.price <= self.bids.best.price and
            self.stop_bids.best.first.order_id < self.bids.best.first.order_id
        ):
            return self.stop_bids, self.offers

        if (
            aggressor.side == Side.BUY and
            self.stop_offers and
            self.stop_offers.best.price <= self.offers.best.price and
            self.stop_offers.best.first.order_id < self.offers.best.first.order_id
        ):
            return self.bids, self.stop_offers

        return self.bids, self.offers

    def _pre_fill(
            self,
            bids: AggregateOrderSide,
            offers: AggregateOrderSide,
            aggressor: Order
    ) -> List[Order]:
        cancels: List[Order] = []

        for plugin in self._plugins:
            cancels += plugin.pre_fill(bids, offers, aggressor)

        return cancels

    def _post_match(self) -> List[Order]:
        cancels: List[Order] = []

        for plugin in self._plugins:
            cancels += plugin.post_match()

        return cancels

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, OrderBookManager) and
            self.bids == other.bids and
            self.offers == other.offers
        )

    def __repr__(self) -> str:
        return f"OrderBook({self.bids}, {self.offers})"

    def __str__(self) -> str:
        return format(self, "")

    def __format__(self, format_spec: str) -> str:
        levels = None if not format_spec else int(format_spec)
        if not (levels is None or levels > 0):
            raise ValueError('levels should be > 0')

        bids, offers = self.book_depth(levels)

        return f'{",".join(map(str, bids))} : {",".join(map(str, offers))}'

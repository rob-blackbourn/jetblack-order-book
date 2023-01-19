"""Order Book"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional, Sequence, Tuple

from .aggregate_order import AggregateOrder
from .aggregate_order_side import AggregateOrderSide
from .fill import Fill
from .limit_order import LimitOrder, Side, Style
from .order_repo import OrderRepo


class OrderBook:
    """An order book"""

    def __init__(
            self,
    ) -> None:
        self._orders = OrderRepo()
        self._sides = {
            Side.BUY: AggregateOrderSide(Side.BUY),
            Side.SELL: AggregateOrderSide(Side.SELL)
        }

    @property
    def bids(self) -> AggregateOrderSide:
        """The bids"""
        return self._sides[Side.BUY]

    @property
    def offers(self) -> AggregateOrderSide:
        """The offers"""
        return self._sides[Side.SELL]

    def book_depth(
            self,
            levels: Optional[int]
    ) -> Tuple[Sequence[AggregateOrder], Sequence[AggregateOrder]]:
        """The best bids and offers.

        Args:
            levels (Optional[int]): An optional book depth.

        Returns:
            Tuple[Sequence[AggregateOrder], Sequence[AggregateOrder]]: The best
                bids and offers.
        """
        return self.bids.orders(levels), self.offers.orders(levels)

    def add_limit_order(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[int], List[Fill], List[int]]:
        """Add a limit order to the order book.

        Args:
            side (Side): Buy or sell.
            price (Decimal): The price at which the order should be executed.
            size (int): The size of the order.

        Returns:
            Tuple[int, List[Fill]]: The order id and any fills that were
            generated.
        """
        order, cancels = self._orders.create(
            side,
            price,
            size,
            style
        )
        for order_id in cancels:
            self.cancel_limit_order(order_id)

        if order is None:
            return None, [], []

        self._sides[order.side].add_limit_order(order)

        # Return the order id and any fills that were generated. The id of the
        # order that instigated the changes is supplied.
        return order.order_id, *self._match(order.order_id, cancels)

    def amend_limit_order(self, order_id: int, size: int) -> None:
        """Amend the size of a limit order.

        Args:
            order_id (int): The order id.
            size (int): The new size of the order.

        Raises:
            ValueError: When the size is less than or equal to 0.
        """
        assert size > 0, "size must be greater than 0"

        order = self._orders.find(order_id)
        self._sides[order.side].amend_limit_order(order, size)

    def cancel_limit_order(self, order_id: int) -> None:
        """Cancel a limit order.

        Args:
            order_id (int): The order id.

        Raises:
            ValueError: If the order cannot be found.
        """
        order = self._orders.find(order_id)
        self._sides[order.side].cancel_limit_order(order)
        self._orders.delete(order)

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
                        self._sides[order.side].cancel_limit_order(order)
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
                    self._orders.delete(self.bids.best.first)
                    self.bids.best.delete_first()

                self.offers.best.first.size -= fill_size
                if self.offers.best.first.size == 0:
                    self._orders.delete(self.offers.best.first)
                    self.offers.best.delete_first()

            # Check if any orders require cancellation.
            cancel_orders = self._post_match_check()
            for order in cancel_orders:
                cancels.append(order.order_id)
                self._sides[order.side].cancel_limit_order(order)

            # if all orders have been executed at this price level remove the
            # price level.
            if self.bids and not self.bids.best:
                self.bids.delete_best()
            if self.offers and not self.offers.best:
                self.offers.delete_best()

        return fills, cancels

    def _pre_fill_check(self) -> List[LimitOrder]:
        cancels: List[LimitOrder] = []
        order = self.bids.best.handle_fill_or_kill(self.offers.best)
        if order is not None:
            cancels.append(order)

        return cancels

    def _post_match_check(self) -> List[LimitOrder]:
        cancels: List[LimitOrder] = []

        if self.bids:
            orders = self.bids.best.find_by_style(Style.IMMEDIATE_OR_CANCEL)
            cancels += orders

        if self.offers:
            orders = self.offers.best.find_by_style(Style.IMMEDIATE_OR_CANCEL)
            cancels += orders

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

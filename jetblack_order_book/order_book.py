"""Order Book"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional, Sequence, Tuple

from .aggregate_order import AggregateOrder
from .aggregate_order_side import AggregateOrderSide
from .fill import Fill
from .limit_order import LimitOrder, Side, Style


class OrderBook:
    """An order book"""

    def __init__(
            self,
    ) -> None:
        self._orders: Dict[int, LimitOrder] = {}
        self._next_order_id = 1
        self._immediate_or_cancel: Dict[Side, AggregateOrder] = {}
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
            Tuple[int, List[Fill], List[int]]: The order id, any fills that were
            generated, and any orders that were cancelled.
        """
        order, cancels = self._create(
            side,
            price,
            size,
            style
        )

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

        order = self._find(order_id)
        self._sides[order.side].amend_limit_order(order, size)

    def cancel_limit_order(self, order_id: int) -> None:
        """Cancel a limit order.

        Args:
            order_id (int): The order id.

        Raises:
            ValueError: If the order cannot be found.
        """
        order = self._find(order_id)
        self._sides[order.side].cancel_limit_order(order)
        self._delete(order)

    def _create(
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

        if order.style == Style.IMMEDIATE_OR_CANCEL:
            cancels += self._post_create_immediate_or_cancel(order)

        return cancels

    def _post_create_immediate_or_cancel(
            self,
            order: LimitOrder
    ) -> List[int]:

        if order.side not in self._immediate_or_cancel:
            self._immediate_or_cancel[order.side] = AggregateOrder(order)
            return []

        if order.price == self._immediate_or_cancel[order.side].price:
            self._immediate_or_cancel[order.side].append(order)
            return []

        cancels: List[int] = list(map(
            lambda x: x.order_id,
            self._immediate_or_cancel[order.side].orders
        ))
        for order_id in cancels:
            self.cancel_limit_order(order_id)
        self._immediate_or_cancel[order.side] = AggregateOrder(order)

        return cancels

    def _find(self, order_id: int) -> LimitOrder:
        return self._orders[order_id]

    def _delete(self, order: LimitOrder) -> None:
        del self._orders[order.order_id]
        if (
                order.side in self._immediate_or_cancel and
                order.order_id in self._immediate_or_cancel[order.side]
        ):
            self._immediate_or_cancel[order.side].cancel(order.order_id)

    def _is_valid(self, side: Side, price: Decimal, style: Style) -> bool:
        if style == Style.IMMEDIATE_OR_CANCEL:
            return self._is_best_immediate_or_cancel(side, price)

        return True

    def _is_best_immediate_or_cancel(self, side: Side, price: Decimal) -> bool:
        if side not in self._immediate_or_cancel:
            return True
        if side == Side.BUY and price >= self._immediate_or_cancel[side].price:
            return True
        if side == Side.SELL and price <= self._immediate_or_cancel[side].price:
            return True
        return False

    def _find_cancellable_orders(self, order: LimitOrder) -> List[int]:
        cancel_orders: List[LimitOrder] = []

        cancel_orders += self._find_cancellable_immediate_or_cancel_orders(
            order
        )

        return [cancel_order.order_id for cancel_order in cancel_orders]

    def _find_cancellable_immediate_or_cancel_orders(
            self,
            order: LimitOrder
    ) -> List[LimitOrder]:
        if (
            (
                order.side in self._immediate_or_cancel
            )
            and
            (
                (
                    order.size == Side.BUY and
                    self._immediate_or_cancel[order.side].price < order.price
                )
                or
                (
                    order.size == Side.SELL and
                    self._immediate_or_cancel[order.side].price < order.price
                )
            )
        ):
            return self._immediate_or_cancel[order.side].orders

        return []

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
                    self._delete(self.bids.best.first)
                    self.bids.best.delete_first()

                self.offers.best.first.size -= fill_size
                if self.offers.best.first.size == 0:
                    self._delete(self.offers.best.first)
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

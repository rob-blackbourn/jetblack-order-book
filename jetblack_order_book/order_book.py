"""Order Book"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional, Sequence, Tuple

from .aggregate_order import AggregateOrder
from .aggregate_order_side import AggregateOrderSide
from .fill import Fill
from .limit_order import LimitOrder
from .order_types import Side


class OrderBook:
    """An order book"""

    def __init__(
            self,
    ) -> None:
        self._orders: Dict[int, LimitOrder] = {}
        self._sides = {
            Side.BUY: AggregateOrderSide(Side.BUY),
            Side.SELL: AggregateOrderSide(Side.SELL)
        }
        self._next_order_id = 1

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
        return self._bids.orders(levels), self._offers.orders(levels)

    def add_limit_order(
            self,
            side: Side,
            price: Decimal,
            size: int
    ) -> Tuple[int, List[Fill]]:
        """Add a limit order to the order book.

        Args:
            side (Side): Buy or sell.
            price (Decimal): The price at which the order should be executed.
            size (int): The size of the order.

        Returns:
            Tuple[int, List[Fill]]: The order id and any fills that were
            generated.
        """
        order = self._create_order(side, price, size)
        self._sides[order.side].add_limit_order(order)

        # Return the order id and any fills that were generated. The id of the
        # order that instigated the changes is supplied.
        return order.order_id, self._match(order.order_id)

    def amend_limit_order(self, order_id: int, size: int) -> None:
        """Amend the size of a limit order.

        Args:
            order_id (int): The order id.
            size (int): The new size of the order.

        Raises:
            ValueError: When the size is less than or equal to 0.
        """
        assert size > 0, "size must be greater than 0"

        order = self._find_order(order_id)
        self._sides[order.side].amend_limit_order(order, size)

    def cancel_limit_order(self, order_id: int) -> None:
        """Cancel a limit order.

        Args:
            order_id (int): The order id.

        Raises:
            ValueError: If the order cannot be found.
        """
        order = self._find_order(order_id)
        self._sides[order.side].cancel_limit_order(order)
        self._delete_order(order)

    @property
    def _bids(self) -> AggregateOrderSide:
        return self._sides[Side.BUY]

    @property
    def _offers(self) -> AggregateOrderSide:
        return self._sides[Side.SELL]

    def _match(self, aggressor_order_id: int) -> List[Fill]:
        """Match bids against offers generating fills.

        Args:
            aggressor_order_id (int): The order id that generated the match.

        Returns:
            List[Fill]: The fills.
        """
        fills: List[Fill] = []
        while (
                self._bids and
                self._offers and
                self._bids.best.price >= self._offers.best.price
        ):
            while self._bids.best and self._offers.best:
                # The price is that of the newest order in case of a cross;
                # where the newest order price exceeds (rather than matched)
                # the best opposing price.
                trade_size = min(
                    self._bids.best.first.size,
                    self._offers.best.first.size
                )
                trade_price = (
                    self._bids.best.first.price
                    if self._bids.best.first.order_id == aggressor_order_id
                    else self._offers.best.first.price
                )

                fills.append(
                    Fill(
                        self._bids.best.first.order_id,
                        self._offers.best.first.order_id,
                        trade_price,
                        trade_size)
                )

                # Decrement the orders by the trade size, then check if the
                # orders have been completely executed.

                self._bids.best.first.size -= trade_size
                if self._bids.best.first.size == 0:
                    del self._orders[self._bids.best.first.order_id]
                    self._bids.best.delete_first()

                self._offers.best.first.size -= trade_size
                if self._offers.best.first.size == 0:
                    del self._orders[self._offers.best.first.order_id]
                    self._offers.best.delete_first()

            # if all orders have been executed at this price level remove the
            # price level.
            if not self._bids.best:
                self._bids.delete_best()
            if not self._offers.best:
                self._offers.delete_best()

        return fills

    def _create_order(
            self,
            side: Side,
            price: Decimal,
            size: int
    ) -> LimitOrder:
        order = LimitOrder(self._next_order_id, side, price, size)
        self._orders[order.order_id] = order
        self._next_order_id += 1
        return order

    def _find_order(self, order_id: int) -> LimitOrder:
        return self._orders[order_id]

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            self._bids == other._bids and
            self._offers == other._offers
        )

    def _delete_order(self, order: LimitOrder) -> None:
        del self._orders[order.order_id]

    def __repr__(self) -> str:
        return f"OrderBook({self._bids}, {self._offers})"

    def __str__(self) -> str:
        return format(self, "")

    def __format__(self, format_spec: str) -> str:
        levels = None if not format_spec else int(format_spec)
        assert levels is None or levels > 0, 'levels should be > 0'
        bids, offers = self.book_depth(levels)
        return f'{",".join(map(str, bids))} : {",".join(map(str, offers))}'

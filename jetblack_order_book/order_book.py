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

    def __init__(
            self,
    ) -> None:
        self.orders: Dict[int, LimitOrder] = {}
        # bids and offers are ordered from low to high.
        self.bids = AggregateOrderSide(Side.BUY)
        self.offers = AggregateOrderSide(Side.SELL)
        self._next_order_id = 1

    def __repr__(self) -> str:
        return f"OrderBook({self.bids}, {self.offers})"

    def __str__(self) -> str:
        return format(self, "")

    def __format__(self, format_spec: str) -> str:
        levels = None if not format_spec else int(format_spec)
        assert levels is None or levels > 0, 'levels should be > 0'
        bids, offers = self.book_depth(levels)
        return f'{",".join(map(str, bids))} : {",".join(map(str, offers))}'

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

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            self.bids == other.bids and
            self.offers == other.offers
        )

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
        # Make the limit order.
        order = LimitOrder(self._next_order_id, side, price, size)
        self.orders[order.order_id] = order
        self._next_order_id += 1

        # Get the orders for the side.
        aggregate_orders_for_side = (
            self.bids if side == Side.BUY
            else self.offers
        )

        aggregate_orders_for_side.add_limit_order(order)

        # Return the order id and any fills that were generated. The id of the
        # order that instigated the changes is supplied.
        return order.order_id, self._match(order.order_id)

    def _match(self, aggressor_order_id: int) -> List[Fill]:
        fills: List[Fill] = []
        while (
                self.bids and
                self.offers and
                self.bids.best.price >= self.offers.best.price
        ):
            while self.bids.best and self.offers.best:
                # The price is that of the newest order in case of a cross;
                # where the newest order price exceeds (rather than matched)
                # the best opposing price.
                trade_size = min(
                    self.bids.best.first.size,
                    self.offers.best.first.size
                )
                trade_price = (
                    self.bids.best.first.price
                    if self.bids.best.first.order_id == aggressor_order_id
                    else self.offers.best.first.price
                )

                fills.append(
                    Fill(
                        self.bids.best.first.order_id,
                        self.offers.best.first.order_id,
                        trade_price,
                        trade_size)
                )

                # Decrement the orders by the trade size, then check if the
                # orders have been completely executed.

                self.bids.best.first.size -= trade_size
                if self.bids.best.first.size == 0:
                    del self.orders[self.bids.best.first.order_id]
                    self.bids.best.delete_first()

                self.offers.best.first.size -= trade_size
                if self.offers.best.first.size == 0:
                    del self.orders[self.offers.best.first.order_id]
                    self.offers.best.delete_first()

            # if all orders have been executed at this price level remove the
            # price level.
            if not self.bids.best:
                self.bids.delete_best()
            if not self.offers.best:
                self.offers.delete_best()

        return fills

    def amend_limit_order(self, order_id: int, size: int) -> None:
        """Amend the size of a limit order.

        Args:
            order_id (int): The order id.
            size (int): The new size of the order.

        Raises:
            ValueError: When the size is less than or equal to 0.
        """
        assert size > 0, "size must be greater than 0"

        # Find the order.
        existing_order = self.orders[order_id]

        # Get the aggregate orders in which the order exists.
        aggregate_orders_for_side = (
            self.bids if existing_order.side == Side.BUY
            else self.offers
        )

        aggregate_orders_for_side.amend_limit_order(existing_order, size)

    def cancel_limit_order(self, order_id: int) -> None:
        """Cancel a limit order.

        Args:
            order_id (int): The order id.

        Raises:
            ValueError: If the order cannot be found.
        """
        existing_order = self.orders[order_id]

        aggregate_orders_for_side = (
            self.bids if existing_order.side == Side.BUY
            else self.offers
        )

        aggregate_orders_for_side.cancel_limit_order(existing_order)

        del self.orders[order_id]

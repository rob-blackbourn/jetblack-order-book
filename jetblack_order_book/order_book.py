"""Order Book"""

from __future__ import annotations

from collections import deque
from decimal import Decimal
from itertools import islice
from typing import Deque, Dict, List, Tuple

from .aggregate_order import AggregateOrder
from .fill import Fill
from .linq import index_of
from .limit_order import LimitOrder
from .order_types import Side


class OrderBook:

    def __init__(
            self,
    ) -> None:
        self.orders: Dict[int, LimitOrder] = {}
        # bids and offers are ordered from low to high.
        self.bids: Deque[AggregateOrder] = deque()
        self.offers: Deque[AggregateOrder] = deque()
        self._next_order_id = 1

    def __repr__(self) -> str:
        return f"OrderBook({self.bids}, {self.offers})"

    def __str__(self) -> str:
        return format(self, "")

    def __format__(self, format_spec: str) -> str:
        levels = None if not format_spec else int(format_spec)
        # pylint: disable=invalid-unary-operand-type
        bids = self.bids if levels is None else tuple(
            islice(self.bids, len(self.bids) - levels, len(self.bids))
        )
        offers = self.offers if levels is None else islice(
            self.offers,
            0,
            levels
        )
        return f'{",".join(map(str, bids))} : {",".join(map(str, offers))}'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            all(a == b for a, b in zip(self.bids, other.bids)) and
            all(a == b for a, b in zip(self.offers, other.offers))
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

        # Find where the order should go.
        index = index_of(
            aggregate_orders_for_side,
            lambda x: x.price >= price
        )
        if index == -1:
            # Add new highest price level.
            aggregate_orders_for_side.append(AggregateOrder(order))
        elif aggregate_orders_for_side[index].price == order.price:
            # Add the order to an existing price level. Adding to the end
            # means newer orders are executed first (time weighted).
            aggregate_orders_for_side[index].append(order)
        else:
            # Insert a new lowest price level
            aggregate_orders_for_side.insert(index, AggregateOrder(order))

        # Return the order id and any fills that were generated. The id of the
        # order that instigated the changes is supplied.
        return order.order_id, self._match(order.order_id)

    def _match(self, aggressor_order_id: int) -> List[Fill]:
        fills: List[Fill] = []
        while (
                self.bids and
                self.offers and
                self.bids[-1].price >= self.offers[0].price
        ):
            # The best bid is the highest price (at the end), while the best
            # offer is the lowest price (at the start).
            best_bids, best_offers = self.bids[-1], self.offers[0]
            while best_bids and best_offers:
                # The aggregate orders are ordered by time, so the first order
                # takes precedence.
                bid, offer = best_bids[0], best_offers[0]

                # The price is that of the newest order in case of a cross;
                # where the newest order price exceeds (rather than matched)
                # the best opposing price.
                trade_size = min(bid.size, offer.size)
                trade_price = (
                    bid.price if bid.order_id == aggressor_order_id
                    else offer.price
                )

                fills.append(
                    Fill(
                        bid.order_id,
                        offer.order_id,
                        trade_price,
                        trade_size)
                )

                # Decrement the orders by the trade size, then check if the
                # orders have been completely executed.

                bid.size -= trade_size
                if bid.size == 0:
                    del best_bids[0]
                    del self.orders[bid.order_id]

                offer.size -= trade_size
                if offer.size == 0:
                    del self.orders[offer.order_id]
                    del best_offers[0]

            # if all orders have been executed at this price level remove the
            # price level.
            if not best_bids:
                del self.bids[-1]
            if not best_offers:
                del self.offers[0]

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

        # Find the position of the order in the aggregate orders.
        index = index_of(
            aggregate_orders_for_side,
            lambda x: x.price == existing_order.price
        )
        if index == -1:
            raise ValueError("no order at this price")

        # Change the size.
        aggregate_orders_for_side[index].change_size(order_id, size)

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

        index = index_of(
            aggregate_orders_for_side,
            lambda x: x.price == existing_order.price
        )
        if index == -1:
            raise KeyError("The aggregate order could not be found")

        aggregate_order = aggregate_orders_for_side[index]
        aggregate_order.cancel(order_id)
        if len(aggregate_order) == 0:
            # If there are no orders left at this price level, delete the
            # aggregate order.
            del aggregate_orders_for_side[index]

        del self.orders[order_id]

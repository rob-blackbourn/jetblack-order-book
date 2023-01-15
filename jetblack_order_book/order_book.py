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
        aggregate_orders = (
            self.bids if side == Side.BUY
            else self.offers
        )

        order = LimitOrder(self._next_order_id, side, price, size)
        self.orders[order.order_id] = order
        self._next_order_id += 1

        index = index_of(
            aggregate_orders,
            lambda x: x.price >= price
        )
        if index == -1:
            # Add new highest price level.
            aggregate_orders.append(AggregateOrder(order))
        elif aggregate_orders[index].price == order.price:
            # Aggregate to an existing price level.
            aggregate_orders[index].append(order)
        else:
            # Insert a new lowest price level
            aggregate_orders.insert(index, AggregateOrder(order))

        return order.order_id, self._match(order.order_id)

    def _match(self, aggressor_order_id: int) -> List[Fill]:
        fills: List[Fill] = []
        while (
                self.bids and
                self.offers and
                self.bids[-1].price >= self.offers[0].price
        ):
            best_bids, best_offers = self.bids[-1], self.offers[0]
            while best_bids and best_offers:
                bid, offer = best_bids.pop(), best_offers.popleft()
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
                bid = bid.replace(size=bid.size - trade_size)
                offer = offer.replace(
                    size=offer.size - trade_size
                )
                if bid.size == 0:
                    del self.orders[bid.order_id]
                else:
                    best_bids.append(bid)
                    self.orders[bid.order_id] = bid

                if offer.size == 0:
                    del self.orders[offer.order_id]
                else:
                    best_offers.appendleft(offer)
                    self.orders[offer.order_id] = offer

            if not best_bids:
                del self.bids[-1]
            if not best_offers:
                del self.offers[0]

        return fills

    def amend_limit_order(self, order_id: int, size: int) -> None:
        assert size > 0, "size must be greater than 0"

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
            raise ValueError("no order at this price")

        aggregate_order = aggregate_orders_for_side[index]
        self.orders[order_id] = aggregate_order.change_size(order_id, size)

    def cancel_limit_order(self, order_id: int) -> None:
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
            raise ValueError("no orders at this price")

        aggregate_order = aggregate_orders_for_side[index]
        aggregate_order.cancel(order_id)
        if len(aggregate_order) == 0:
            del aggregate_orders_for_side[index]
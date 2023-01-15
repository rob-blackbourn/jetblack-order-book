"""Order Book"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Tuple

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
        self.bids: List[AggregateOrder] = []
        self.offers: List[AggregateOrder] = []
        self._next_order_id = 1

    def __repr__(self) -> str:
        return f"OrderBook({self.bids}, {self.offers})"

    def __str__(self) -> str:
        return format(self, "")

    def __format__(self, format_spec: str) -> str:
        levels = None if not format_spec else int(format_spec)
        # pylint: disable=invalid-unary-operand-type
        bids = self.bids if levels is None else self.bids[-levels:]
        offers = self.offers if levels is None else self.offers[:levels]
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
        self._next_order_id += 1

        index = index_of(
            aggregate_orders,
            lambda x: x.price < price
        )
        if index == -1:
            # Add new highest price level.
            aggregate_orders.append(AggregateOrder(order))
        elif aggregate_orders[index].price == order.price:
            # Aggregate to an existing price level.
            aggregate_orders[index] += order
        else:
            # Insert a new lowest price level
            aggregate_orders.insert(index, AggregateOrder(order))

        return order.order_id, self.match()

    def match(self) -> List[Fill]:
        fills: List[Fill] = []
        while (
                self.bids and
                self.offers and
                self.bids[-1].price >= self.offers[0].price
        ):
            best_bids, best_offers = self.bids[-1], self.offers[0]
            while best_bids and best_offers:
                best_bid, best_offer = best_bids.pop(0), best_offers.pop(0)
                trade_size = min(best_bid.size, best_offer.size)
                fills.append(
                    Fill(
                        best_bid.order_id,
                        best_offer.order_id,
                        best_bid.price,
                        trade_size)
                )
                best_bid = best_bid.replace(size=best_bid.size - trade_size)
                best_offer = best_bid.replace(
                    size=best_offer.size - trade_size
                )
                if best_bid.size != 0:
                    best_bids.insert(0, best_bid)
                if best_offer.size != 0:
                    best_offers.insert(0, best_offer)

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

"""Order Book"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Tuple

from .aggregate_order import AggregateOrder
from .linq import index_of
from .limit_order import LimitOrder
from .order_types import Side


class Fill:

    def __init__(
            self,
            buy_order_id: int,
            sell_order_id: int,
            price: Decimal,
            size: int
    ) -> None:
        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.price = price
        self.size = size


class OrderBook:

    def __init__(
            self,
    ) -> None:
        self.orders: Dict[int, LimitOrder] = {}
        self.buys: List[AggregateOrder] = []
        self.sells: List[AggregateOrder] = []
        self._next_order_id = 0

    def __repr__(self) -> str:
        return f"OrderBook({self.buys}, {self.sells})"

    def __str__(self) -> str:
        return format(self, "")

    def __format__(self, format_spec: str) -> str:
        levels = None if not format_spec else int(format_spec)
        # pylint: disable=invalid-unary-operand-type
        buys = self.buys if levels is None else self.buys[-levels:]
        sells = self.sells if levels is None else self.sells[:levels]
        return f'{",".join(map(str, buys))} : {",".join(map(str, sells))}'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            all(a == b for a, b in zip(self.buys, other.buys)) and
            all(a == b for a, b in zip(self.sells, other.sells))
        )

    def add_limit_order(
            self,
            side: Side,
            price: Decimal,
            size: int
    ) -> Tuple[int, List[Fill]]:
        aggregate_orders = (
            self.buys if side == Side.BUY
            else self.sells
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

        fills: List[Fill] = []
        while (
                self.buys and
                self.sells and
                self.buys[-1].price >= self.sells[0].price
        ):
            buys, sells = self.buys[-1], self.sells[0]
            while buys and sells:
                buy, sell = buys[0], sells[0]
                trade_size = min(buy.size, sell.size)
                fills.append(
                    Fill(
                        buy.order_id,
                        sell.order_id,
                        buy.price,
                        trade_size)
                )
                buy.size -= trade_size
                sell.size -= sell.size
                if buy.size == 0:
                    del buys[0]
                if sells.size == 0:
                    del sells[0]

        return order.order_id, fills

    def amend_limit_order(self, order_id: int, size: int) -> None:
        assert size > 0, "size must be greater than 0"

        order = self.orders[order_id]

        aggregate_orders = (
            self.buys if order.side == Side.BUY
            else self.sells
        )

        index = index_of(
            aggregate_orders,
            lambda x: x.price == order.price
        )
        if index == -1:
            raise ValueError("no order at this price")

        aggregate_order = aggregate_orders[index]
        aggregate_order[order_id].size = order.size

    def cancel_limit_order(self, order_id: int) -> None:
        order = self.orders[order_id]

        aggregate_orders = (
            self.buys if order.side == Side.BUY
            else self.sells
        )

        index = index_of(
            aggregate_orders,
            lambda x: x.price == order.price
        )
        if index == -1:
            raise ValueError("no orders at this price")

        aggregate_order = aggregate_orders[index]
        if order_id not in aggregate_order:
            raise KeyError("invalid order id")

        del aggregate_order[order_id]

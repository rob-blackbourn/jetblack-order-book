"""Order Book"""

from __future__ import annotations

from typing import List

from .aggregate_order import AggregateOrder
from .messages import Message, Side, EventType
from .linq import index_of
from .order import Order


class OrderBook:

    def __init__(
            self,
            buys: List[AggregateOrder],
            sells: List[AggregateOrder]
    ) -> None:
        self.buys = buys
        self.sells = sells

        self._handlers = {
            EventType.SUBMIT: self._handle_submit,
            EventType.CANCEL: self._handle_cancel,
            EventType.DELETE: self._handle_delete,
            EventType.EXECUTE_VISIBLE: self._handle_execute_visible,
            EventType.EXECUTE_HIDDEN: self._handle_execute_hidden,
            EventType.CROSS: self._handle_cross,
            EventType.HALT: self._handle_halt,
        }

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

    def copy(self) -> OrderBook:
        return OrderBook(
            [order.copy() for order in self.buys],
            [order.copy() for order in self.sells]
        )

    def process(self, message: Message) -> OrderBook:
        return self._handlers[message.event_type](message)

    def _handle_submit(self, message: Message) -> OrderBook:
        order = Order(message.price, message.size, message.order_id)

        order_book = self.copy()
        aggregate_orders = (
            order_book.buys if message.side == Side.BUY
            else order_book.sells
        )

        index = index_of(
            aggregate_orders,
            lambda x: order.price <= x.price
        )
        if index == -1:
            aggregate_orders.append(AggregateOrder([order]))
        elif aggregate_orders[index].price == order.price:
            aggregate_orders[index] += order
        else:
            aggregate_orders.insert(index, AggregateOrder([order]))
            # del aggregate_orders[0 if message.side == Side.BUY else -1]

        return order_book

    def _handle_cancel(self, message: Message) -> OrderBook:
        # Cancellation (partial deletion of a limit order)
        order_book = self.copy()
        aggregate_orders = (
            order_book.buys if message.side == Side.BUY
            else order_book.sells
        )

        index = index_of(
            aggregate_orders,
            lambda x: x.price == message.price
        )
        if index == -1:
            raise ValueError("no order at this price")

        aggregate_order = aggregate_orders[index]
        order_id = message.order_id if message.order_id in aggregate_order else -1
        aggregate_order[order_id].size -= message.size
        if aggregate_order[order_id].size == 0:
            raise ValueError("partial delete was the whole size")

        return order_book

    def _handle_delete(self, message: Message) -> OrderBook:
        # Deletion (total deletion of a limit order)
        order_book = self.copy()
        aggregate_orders = (
            order_book.buys if message.side == Side.BUY
            else order_book.sells
        )

        index = index_of(
            aggregate_orders,
            lambda x: x.price == message.price
        )
        if index == -1:
            raise ValueError("no order at this price")

        aggregate_order = aggregate_orders[index]
        if message.order_id in aggregate_order:
            if aggregate_order[message.order_id].size != message.size:
                raise ValueError("invalid order size for delete")
            del aggregate_order[message.order_id]
        elif -1 in aggregate_order:
            if aggregate_order[-1].size < message.size:
                raise ValueError("invalid order size for anonymous delete")
            elif aggregate_order[-1].size == message.size:
                del aggregate_order[-1]
            else:
                aggregate_order[-1].size -= message.size

        if aggregate_order.size == 0:
            del aggregate_orders[index]

        return order_book

    def _handle_execute_visible(self, message: Message) -> OrderBook:
        raise NotImplementedError("execute visible")

    def _handle_execute_hidden(self, message: Message) -> OrderBook:
        raise NotImplementedError("execute hidden")

    def _handle_cross(self, message: Message) -> OrderBook:
        raise NotImplementedError("cross")

    def _handle_halt(self, message: Message) -> OrderBook:
        raise NotImplementedError("halt")

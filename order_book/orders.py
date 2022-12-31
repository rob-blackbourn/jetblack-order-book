"""Order Book"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from typing import List, Iterator

from .messages import Message, Side, EventType
from .linq import index_of


class Order:

    def __init__(self, price: Decimal, size: int) -> None:
        self.price = price
        self.size = size

    def __repr__(self) -> str:
        return f"Order({self.price}, {self.size})"

    def __str__(self) -> str:
        return f"{self.price}x{self.size}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Order) and
            self.price == other.price and
            self.size == other.size
        )


class OrderBook:

    def __init__(
            self,
            buys: List[Order],
            sells: List[Order],
            levels: int
    ) -> None:
        self.buys = buys
        self.sells = sells
        self.levels = levels

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
        return f'{",".join(map(str, self.buys))} : {",".join(map(str, self.sells))}'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, OrderBook) and
            all(a == b for a, b in zip(self.buys, other.buys)) and
            all(a == b for a, b in zip(self.sells, other.sells))
        )

    def copy(self) -> OrderBook:
        return OrderBook(
            [Order(order.price, order.size) for order in self.buys],
            [Order(order.price, order.size) for order in self.sells],
            self.levels
        )

    def process(self, message: Message) -> OrderBook:
        return self._handlers[message.event_type](message)

    def _handle_submit(self, message: Message) -> OrderBook:
        order = Order(message.price, message.size)

        book = self.copy()
        orders = book.buys if message.side == Side.BUY else book.sells

        index = index_of(
            orders,
            lambda x: order.price <= x.price
        )
        if index == -1:
            orders.append(order)
        elif orders[index].price == order.price:
            orders[index].size += order.size
        else:
            orders.insert(index, order)
            del orders[0 if message.side == Side.BUY else -1]

        return book

    def _handle_cancel(self, message: Message) -> OrderBook:
        raise NotImplementedError("cancel")

    def _handle_delete(self, message: Message) -> OrderBook:
        raise NotImplementedError("delete")

    def _handle_execute_visible(self, message: Message) -> OrderBook:
        raise NotImplementedError("execute visible")

    def _handle_execute_hidden(self, message: Message) -> OrderBook:
        raise NotImplementedError("execute hidden")

    def _handle_cross(self, message: Message) -> OrderBook:
        raise NotImplementedError("cross")

    def _handle_halt(self, message: Message) -> OrderBook:
        raise NotImplementedError("halt")


def iter_order_book(file_name: Path, levels: int) -> Iterator[OrderBook]:
    with open(file_name, newline='', encoding='ascii') as fp:
        reader = csv.reader(fp)
        for line in reader:
            yield OrderBook(
                list(reversed([
                    Order(Decimal(line[level+2]) / 10000, int(line[level+3]))
                    for level in range(0, levels*4, 4)
                ])),
                [
                    Order(Decimal(line[level+0]) / 10000, int(line[level+1]))
                    for level in range(0, levels*4, 4)
                ],
                levels
            )


def load_order_book(file_name: Path, levels: int):
    for order_book in iter_order_book(file_name, levels):
        print(order_book)

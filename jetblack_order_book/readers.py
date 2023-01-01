"""Readers"""

import csv
from decimal import Decimal
from pathlib import Path
from typing import Iterator

from .messages import Message, EventType, Side
from .order_book import OrderBook
from .aggregate_order import AggregateOrder


def iter_order_book(file_name: Path, levels: int) -> Iterator[OrderBook]:
    with open(file_name, newline='', encoding='ascii') as fp:
        reader = csv.reader(fp)
        for line in reader:
            yield OrderBook(
                list(reversed([
                    AggregateOrder.create(
                        Decimal(line[level+2]) / 10000,
                        int(line[level+3]),
                        -1
                    )
                    for level in range(0, levels*4, 4)
                ])),
                [
                    AggregateOrder.create(
                        Decimal(line[level+0]) / 10000,
                        int(line[level+1]),
                        -1
                    )
                    for level in range(0, levels*4, 4)
                ],
            )


def load_order_book(file_name: Path, levels: int):
    for order_book in iter_order_book(file_name, levels):
        print(order_book)


def iter_messages(file_name: Path) -> Iterator[Message]:
    with open(file_name, newline='', encoding='ascii') as fp:
        reader = csv.reader(fp)
        for time, event_type, order_id, size, price, side in reader:
            yield Message(
                float(time),
                EventType(int(event_type)),
                int(order_id),
                int(size),
                Decimal(price) / 10000,
                Side(int(side))
            )


def load_messages(file_name: Path):
    for message in iter_messages(file_name):
        print(message)

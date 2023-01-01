"""Messages"""

import csv
from decimal import Decimal
from enum import IntEnum
from pathlib import Path
from typing import Iterator


class EventType(IntEnum):
    SUBMIT = 1  # Submission of a new limit order
    CANCEL = 2  # Cancellation (partial deletion of a limit order)
    DELETE = 3  # Deletion (total deletion of a limit order)
    EXECUTE_VISIBLE = 4  # Execution of a visible limit order
    EXECUTE_HIDDEN = 5  # Execution of a hidden limit order
    CROSS = 6  # Indicates a cross trade, e.g. auction trade
    HALT = 7  # Trading halt indicator (detailed information below)


class Side(IntEnum):
    BUY = 1
    SELL = -1


class Message:

    def __init__(
            self,
            time: float,
            event_type: EventType,
            order_id: int,
            size: int,
            price: Decimal,
            side: Side
    ) -> None:
        self.time = time
        self.event_type = event_type
        self.order_id = order_id
        self.size = size
        self.price = price
        self.side = side

    def __repr__(self) -> str:
        return f"Message({self.time}, {self.event_type}, {self.order_id}, {self.size}, {self.price}, {self.side})"

    def __str__(self) -> str:
        return f"{self.event_type.name}[{self.order_id}]: {self.side.name} {self.price}x{self.size}"

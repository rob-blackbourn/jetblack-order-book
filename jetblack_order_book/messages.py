"""Messages"""

from decimal import Decimal

from .order_types import EventType, Side


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

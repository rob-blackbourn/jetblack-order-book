"""Limit Order"""

from __future__ import annotations

from decimal import Decimal

from .order_types import Side


class LimitOrder:
    """A limit order is an order which gets executed at a given price"""

    def __init__(
            self,
            order_id: int,
            side: Side,
            price: Decimal,
            size: int
    ) -> None:
        """Initialise a limit order.

        The order_id is an ordinal integer which represents the order in which
        orders are placed.

        Args:
            order_id (int): The order id.
            side (Side): Buy or sell.
            price (Decimal): The price at which the order can be executed.
            size (int): The order size.
        """
        self._order_id = order_id
        self._side = side
        self._price = price
        self.size = size  # The size is mutable.

    @property
    def order_id(self) -> int:
        """The id of the order.

        Returns:
            int: The order id.
        """
        return self._order_id

    @property
    def side(self) -> Side:
        """The side for which the order is for; i.e. buy or sell.

        Returns:
            Side: The side of the order.
        """
        return self._side

    @property
    def price(self) -> Decimal:
        """The price at which the order can be filled.

        Returns:
            Decimal: The limit price.
        """
        return self._price

    def __repr__(self) -> str:
        return f"LimitOrder({self._order_id}, {self._side}, {self._price}, {self.size})"

    def __str__(self) -> str:
        return f"{self.price}x{self.size}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, LimitOrder) and
            self.order_id == other.order_id and
            self.side == other.side and
            self.price == other.price and
            self.size == other.size

        )

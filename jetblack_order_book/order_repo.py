"""Order manager"""

from decimal import Decimal
from typing import Dict

from .limit_order import LimitOrder, Side


class OrderRepo:
    """An order manager"""

    def __init__(self) -> None:
        self._orders: Dict[int, LimitOrder] = {}
        self._next_order_id = 1

    def create(
            self,
            side: Side,
            price: Decimal,
            size: int
    ) -> LimitOrder:
        """Create a new order.

        Args:
            side (Side): Buy or sell.
            price (Decimal): The price.
            size (int): The size.

        Returns:
            LimitOrder: A new limit order.
        """
        order = LimitOrder(self._next_order_id, side, price, size)
        self._orders[order.order_id] = order
        self._next_order_id += 1
        return order

    def find(self, order_id: int) -> LimitOrder:
        """Find an order.

        Args:
            order_id (int): The order id.

        Returns:
            LimitOrder: The order.
        """
        return self._orders[order_id]

    def delete(self, order: LimitOrder) -> None:
        """Delete an order.

        Args:
            order (LimitOrder): The order to delete.
        """
        del self._orders[order.order_id]

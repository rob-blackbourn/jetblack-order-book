"""Order manager"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from .limit_order import LimitOrder, Side, Style
from .aggregate_order import AggregateOrder


class OrderRepo:
    """An order manager"""

    def __init__(self) -> None:
        self._orders: Dict[int, LimitOrder] = {}
        self._next_order_id = 1
        self._immediate_or_cancel: Dict[Side, AggregateOrder] = {}

    def create(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[LimitOrder], List[int]]:
        """Create a new order.

        Args:
            side (Side): Buy or sell.
            price (Decimal): The price.
            size (int): The size.
            style (Style): The style.

        Returns:
            LimitOrder: A new limit order.
        """
        if not self.is_valid(side, price, style):
            return None, []

        order = LimitOrder(self._next_order_id, side, price, size, style)
        self._orders[order.order_id] = order
        self._next_order_id += 1

        cancellable_orders: List[int] = []

        if style == Style.IMMEDIATE_OR_CANCEL:
            if side not in self._immediate_or_cancel:
                self._immediate_or_cancel[side] = AggregateOrder(order)
            else:
                if price != self._immediate_or_cancel[side].price:
                    cancellable_orders += list(map(
                        lambda x: x.order_id,
                        self._immediate_or_cancel[side].orders
                    ))
                    self._immediate_or_cancel[side] = AggregateOrder(order)
                else:
                    self._immediate_or_cancel[side].append(order)

        return order, cancellable_orders

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
        if (
                order.side in self._immediate_or_cancel and
                order.order_id in self._immediate_or_cancel[order.side]
        ):
            self._immediate_or_cancel[order.side].cancel(order.order_id)

    def is_valid(self, side: Side, price: Decimal, style: Style) -> bool:
        if style == Style.IMMEDIATE_OR_CANCEL:
            return self._is_best_immediate_or_cancel(side, price)

        return True

    def _is_best_immediate_or_cancel(self, side: Side, price: Decimal) -> bool:
        if side not in self._immediate_or_cancel:
            return True
        if side == Side.BUY and price >= self._immediate_or_cancel[side].price:
            return True
        if side == Side.SELL and price <= self._immediate_or_cancel[side].price:
            return True
        return False

    def _find_cancellable_orders(self, order: LimitOrder) -> List[int]:
        cancel_orders: List[LimitOrder] = []

        cancel_orders += self._find_cancellable_immediate_or_cancel_orders(
            order
        )

        return [cancel_order.order_id for cancel_order in cancel_orders]

    def _find_cancellable_immediate_or_cancel_orders(
            self,
            order: LimitOrder
    ) -> List[LimitOrder]:
        if (
            (
                order.side in self._immediate_or_cancel
            )
            and
            (
                (
                    order.size == Side.BUY and
                    self._immediate_or_cancel[order.side].price < order.price
                )
                or
                (
                    order.size == Side.SELL and
                    self._immediate_or_cancel[order.side].price < order.price
                )
            )
        ):
            return self._immediate_or_cancel[order.side].orders

        return []

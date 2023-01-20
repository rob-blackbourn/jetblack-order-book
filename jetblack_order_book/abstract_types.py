"""Abstract Types"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from decimal import Decimal
from typing import List, Optional, Sequence, Tuple

from .aggregate_order import AggregateOrder
from .aggregate_order_side import AggregateOrderSide
from .fill import Fill
from .limit_order import LimitOrder, Side, Style


class AbstractOrderBook(metaclass=ABCMeta):
    """An abstract order book"""

    @property
    @abstractmethod
    def bids(self) -> AggregateOrderSide:
        """The bids"""

    @property
    @abstractmethod
    def offers(self) -> AggregateOrderSide:
        """The offers"""

    @abstractmethod
    def book_depth(
            self,
            levels: Optional[int]
    ) -> Tuple[Sequence[AggregateOrder], Sequence[AggregateOrder]]:
        """The best bids and offers.

        Args:
            levels (Optional[int]): An optional book depth.

        Returns:
            Tuple[Sequence[AggregateOrder], Sequence[AggregateOrder]]: The best
                bids and offers.
        """

    @abstractmethod
    def add_limit_order(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[int], List[Fill], List[int]]:
        """Add a limit order to the order book.

        Args:
            side (Side): Buy or sell.
            price (Decimal): The price at which the order should be executed.
            size (int): The size of the order.

        Returns:
            Tuple[int, List[Fill], List[int]]: The order id, any fills that were
            generated, and any orders that were cancelled.
        """

    @abstractmethod
    def amend_limit_order(self, order_id: int, size: int) -> None:
        """Amend the size of a limit order.

        Args:
            order_id (int): The order id.
            size (int): The new size of the order.

        Raises:
            ValueError: When the size is less than or equal to 0.
        """

    @abstractmethod
    def cancel_limit_order(self, order_id: int) -> None:
        """Cancel a limit order.

        Args:
            order_id (int): The order id.

        Raises:
            ValueError: If the order cannot be found.
        """


class AbstractOrderBookManager(AbstractOrderBook):
    """An order book manager"""

    @abstractmethod
    def side(self, side: Side) -> AggregateOrderSide:
        """Return the side of the order book.

        Args:
            side (Side): The side required

        Returns:
            AggregateOrderSide: The aggregate order side.
        """

    @abstractmethod
    def create(
            self,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[LimitOrder], List[int]]:
        """Create a limit order.

        Args:
            side (Side): The side.
            price (Decimal): The price.
            size (int): The size.
            style (Style): The style.

        Returns:
            Tuple[Optional[LimitOrder], List[int]]: A limit order or None if
                the order was invalid, and a list of cancelled orders generated
                by the new order.
        """

    @abstractmethod
    def find(self, order_id: int) -> LimitOrder:
        """Find an order.

        Args:
            order_id (int): The order id.

        Returns:
            LimitOrder: The order for the order id.
        """

    @abstractmethod
    def delete(self, order: LimitOrder) -> None:
        """Delete an order.

        Args:
            order (LimitOrder): The order to delete.
        """


class AbstractOrderBookManagerPlugin(metaclass=ABCMeta):
    """An abstract plugin for order book managers"""

    def __init__(self, manager: AbstractOrderBookManager) -> None:
        self.manager = manager

    @property
    @abstractmethod
    def valid_styles(self) -> Sequence[Style]:
        """Return the valid styles for the plugin

        Returns:
            Sequence[Style]: A sequence of supported styles
        """

    # pylint: disable=unused-argument
    def pre_create(self, side: Side, price: Decimal, style: Style) -> bool:
        """A hook called before order creation. If the method returns False
        creation is abandoned.

        Args:
            side (Side): The side.
            price (Decimal): The price.
            style (Style): The style.

        Returns:
            bool: True if the create can continue; otherwise False.
        """
        return True

    def post_create(self, order: LimitOrder) -> List[int]:
        """A hook called after create.

        If the hook returns orders, these orders will be cancelled, and creation
        will continue.

        Args:
            order (LimitOrder): The new order.

        Returns:
            List[int]: A list of order ids invalidated by the new order.
        """
        return []

    def post_delete(self, order: LimitOrder) -> None:
        """A hook called after delete.

        This hook can be used to clean up any locally cached data regarding the
        deleted order.

        Args:
            order (LimitOrder): The order to delete.
        """
        return

    def pre_fill(self, aggressor_id) -> List[LimitOrder]:
        """A hook called before filling an order.

        If the hook returns orders, these orders will be cancelled and the fill
        will be aborted.

        Args:
            aggressor_id (int): The order id of the aggressor.

        Returns:
            List[LimitOrder]: A list of cancellable orders.
        """
        return []

    def post_match(self) -> List[LimitOrder]:
        """A hook called after a match.

        If this hook returns orders, these orders will be cancelled. This can
        be used to clean up orders which are no longer valid. For example any
        "immediate or cancel" orders that were not matched should be cancelled.

        Returns:
            List[LimitOrder]: A list of cancellable orders.
        """
        return []

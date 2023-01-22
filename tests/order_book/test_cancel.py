"""Tests for cancelling orders"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Side, Style


def test_cancel_order():
    """
    An order can be cancelled.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    # Add two buy orders at the same price
    order_book.add_order(Side.BUY, Decimal('10.5'), 10, Style.LIMIT)
    order_book.add_order(Side.SELL, Decimal('10.6'), 10, Style.LIMIT)
    sell2, _, _ = order_book.add_order(
        Side.SELL,
        Decimal('10.6'),
        5,
        Style.LIMIT
    )

    assert str(
        order_book
    ) == '10.5x10 : 10.6x15', "the order book should represent the orders"

    assert sell2 is not None
    order_book.cancel_order(sell2)
    assert str(
        order_book
    ) == '10.5x10 : 10.6x10', "The order should be removed from the order book"

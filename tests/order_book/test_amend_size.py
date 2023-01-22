"""Tests for the amend size"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Side, Style


def test_amend_size():
    """
    The size of a limit order can be changed.
    """

    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    order_book.add_limit_order(
        Side.BUY,
        Decimal('10.5'),
        10,
        Style.LIMIT
    )
    sell2, _, _ = order_book.add_limit_order(
        Side.SELL,
        Decimal('10.6'),
        10,
        Style.LIMIT
    )

    assert str(
        order_book
    ) == '10.5x10 : 10.6x10', "the order book should represent the orders"

    assert sell2 is not None
    order_book.amend_limit_order(sell2, 5)
    assert str(
        order_book
    ) == '10.5x10 : 10.6x5', "the order book should show the change in size"

"""Tests for partial fills"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side, Style


def test_partial_fill():
    """
    A partial fill is an order which matches less than the full amount of the
    matched order, leaving som of the matched order in the book.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : '

    buy1, _, _ = order_book.add_order(
        Side.BUY,
        Decimal('10.5'),
        10,
        Style.LIMIT
    )
    sell1, fills, _ = order_book.add_order(
        Side.SELL,
        Decimal('10.5'),
        5,
        Style.LIMIT
    )

    assert buy1 is not None and sell1 is not None and fills == [
        Fill(buy1, sell1, Decimal('10.5'), 5)
    ]
    assert str(order_book) == '10.5x5 : '

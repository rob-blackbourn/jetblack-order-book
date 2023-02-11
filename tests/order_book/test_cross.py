"""Tests for orders that cross"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side, Style


def test_cross():
    """
    A cross occurs when a sell/buy order is placed at a price below/above
    the best bid/offer. In this case the price of the sell/buy is used, rather
    than the matched price.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    buy1, _, _ = order_book.add_order(
        Side.BUY,
        Decimal('10.5'),
        5,
        Style.LIMIT
    )
    buy2, _, _ = order_book.add_order(
        Side.BUY,
        Decimal('11.0'),
        10,
        Style.LIMIT
    )
    sell1, fills, _ = order_book.add_order(
        Side.SELL,
        Decimal('10.0'),
        15,
        Style.LIMIT
    )

    assert buy1 is not None and sell1 is not None and buy2 is not None and fills == [
        Fill(buy2, sell1, Decimal('10.0'), 10),
        Fill(buy1, sell1, Decimal('10.0'), 5),
    ], "fills should have price of the sell"
    assert str(order_book) == ' : ', "the order book should be empty"

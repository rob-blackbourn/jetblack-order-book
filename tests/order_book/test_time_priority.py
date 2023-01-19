"""Tests for time priority ordering"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side, Style


def test_time_priority():
    """
    Orders at the same price should be executed in the order they are received.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    # Add two buy orders at the same price
    buy1, _, _ = order_book.add_limit_order(
        Side.BUY,
        Decimal('10.5'),
        10,
        Style.VANILLA
    )
    buy2, _, _ = order_book.add_limit_order(
        Side.BUY, Decimal('10.5'),
        5,
        Style.VANILLA
    )

    # Add a sell for the same price with a greater total size
    sell, fills, _ = order_book.add_limit_order(
        Side.SELL,
        Decimal('10.5'),
        20,
        Style.VANILLA
    )

    assert buy1 is not None and sell is not None and buy2 is not None and fills == [
        Fill(buy1, sell, Decimal('10.5'), 10),
        Fill(buy2, sell, Decimal('10.5'), 5),
    ], "the fills should have been made in the order they were placed"

    assert str(order_book) == ' : 10.5x5', "all buys should have been matched"

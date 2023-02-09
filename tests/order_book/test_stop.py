"""Tests for stops"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side, Style


def test_stop_sell():
    """
    A partial fill is an order which matches less than the full amount of the
    matched order, leaving som of the matched order in the book.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : '

    # Add a buy of 5 at 10.
    buy1, fills, cancels = order_book.add_order(
        Side.BUY,
        Decimal('10'),
        5,
        Style.LIMIT
    )
    assert buy1 is not None
    assert not fills, "should be no fills"
    assert not cancels, "should be no cancels"

    # Sell if the price drops to 8
    sell_stop, _, _ = order_book.add_order(
        Side.SELL,
        Decimal('8'),
        5,
        Style.STOP
    )
    assert sell_stop is not None
    assert not fills, "should be no fills"
    assert not cancels, "should be no cancels"

    # Buy at the stop.
    buy2, fills, cancels = order_book.add_order(
        Side.BUY,
        Decimal('8'),
        5,
        Style.LIMIT
    )
    assert buy2 is not None
    assert fills == [
        Fill(buy2, sell_stop, Decimal('8'), 5)
    ], "should fill with the stop"
    assert not cancels, "should be no cancels"

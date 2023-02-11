"""Tests for stops"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side, Style


def test_stop_sell():
    """
    A sell stop order.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : '

    # Add a limit buy order at 10.
    buy1, fills1, cancels1 = order_book.add_order(
        Side.BUY,
        Decimal('10'),
        5,
        Style.LIMIT
    )
    assert buy1 is not None
    assert not fills1, "should be no fills"
    assert not cancels1, "should be no cancels"

    # Add a sell stop order at 8.
    sell2, fills2, cancels2 = order_book.add_order(
        Side.SELL,
        Decimal('8'),
        5,
        Style.STOP
    )
    assert sell2 is not None
    assert not fills2, "should be no fills"
    assert not cancels2, "should be no cancels"

    # Add a sell limit order at 10.
    sell3, fills3, cancels3 = order_book.add_order(
        Side.SELL,
        Decimal('10'),
        5,
        Style.LIMIT
    )
    assert sell3 is not None
    assert fills3 == [
        Fill(buy1, sell3, Decimal('10'), 5)
    ], "should fill the limit orders"
    assert not cancels3, "should be no cancels"

    # Add a buy limit order at8 (triggering the stop).
    buy4, fills4, cancels4 = order_book.add_order(
        Side.BUY,
        Decimal('8'),
        5,
        Style.LIMIT
    )
    assert buy4 is not None
    assert fills4 == [
        Fill(buy4, sell2, Decimal('8'), 5)
    ], "should fill with the stop"
    assert not cancels4, "should be no cancels"


def test_stop_buy():
    """
    A buy stop order.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : '

    # Add a sell limit order at 8.
    sell1, fills1, cancels1 = order_book.add_order(
        Side.SELL,
        Decimal('8'),
        5,
        Style.LIMIT
    )
    assert sell1 is not None
    assert not fills1, "should be no fills"
    assert not cancels1, "should be no cancels"

    # Add a buy stop order at 10.
    buy2, fills2, cancels2 = order_book.add_order(
        Side.BUY,
        Decimal('10'),
        5,
        Style.STOP
    )
    assert buy2 is not None
    assert not fills2, "should be no fills"
    assert not cancels2, "should be no cancels"

    # Add a buy limit order at 8.
    buy3, fills3, cancels3 = order_book.add_order(
        Side.BUY,
        Decimal('8'),
        5,
        Style.LIMIT
    )
    assert buy3 is not None
    assert fills3 == [
        Fill(buy3, sell1, Decimal('8'), 5)
    ], "should fill the limit orders"
    assert not cancels3, "should be no cancels"

    # Add a sell limit order at 10 (triggering the stop).
    sell4, fills4, cancels4 = order_book.add_order(
        Side.SELL,
        Decimal('10'),
        5,
        Style.LIMIT
    )
    assert sell4 is not None
    assert fills4 == [
        Fill(buy2, sell4, Decimal('10'), 5)
    ], "should fill with the stop"
    assert not cancels4, "should be no cancels"

"""Tests for immediate-or-cancel orders"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side, Style


def test_immediate_or_cancel_buys():
    """Test buys for order style immediate-or-cancel"""

    order_book = OrderBook()

    buy_id1, fills, cancels = order_book.add_order(
        Side.BUY,
        Decimal('10'),
        10,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert buy_id1 is not None, "should generate order"
    assert not fills, "should not generate fills"
    assert not cancels, "should not generate cancels"

    buy_id, fills, cancels = order_book.add_order(
        Side.BUY,
        Decimal('9'),
        10,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert buy_id is None, "should not generate order"
    assert not fills, "should not generate fills"
    assert not cancels, "should not generate cancels"

    buy_id2, _, cancels = order_book.add_order(
        Side.BUY,
        Decimal('10'),
        10,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert buy_id2 is not None, "should generate order"
    assert not fills, "should not generate fills"
    assert not cancels, "should not generate cancels"

    buy_id3, fills, cancels = order_book.add_order(
        Side.BUY,
        Decimal('11'),
        10,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert buy_id3 is not None, "should generate buy order"
    assert not fills, "should not generate fills"
    assert cancels == [
        buy_id1,
        buy_id2
    ], "higher priced buy should cancel previous buys"

    sell_id, fills, cancels = order_book.add_order(
        Side.SELL,
        Decimal('11'),
        5,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert sell_id is not None, "should generate sell order"
    assert fills == [
        Fill(buy_id3, sell_id, Decimal('11'), 5)
    ]
    assert cancels == [buy_id3], "should cancel the partially unfilled buy"

    assert str(order_book) == ' : ', "the order book should be empty"


def test_immediate_or_cancel_sells():
    """Test sells for order style immediate-or-cancel"""

    order_book = OrderBook()

    sell_id1, fills, cancels = order_book.add_order(
        Side.SELL,
        Decimal('11'),
        10,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert sell_id1 is not None, "should generate order"
    assert not fills, "should not generate fills"
    assert not cancels, "should not generate cancels"

    sell_id, fills, cancels = order_book.add_order(
        Side.SELL,
        Decimal('12'),
        10,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert sell_id is None, "should not generate order"
    assert not fills, "should not generate fills"
    assert not cancels, "should not generate cancels"

    sell_id2, _, cancels = order_book.add_order(
        Side.SELL,
        Decimal('11'),
        10,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert sell_id2 is not None, "should generate order"
    assert not fills, "should not generate fills"
    assert not cancels, "should not generate cancels"

    sell_id3, fills, cancels = order_book.add_order(
        Side.SELL,
        Decimal('10'),
        10,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert sell_id3 is not None, "should generate buy order"
    assert not fills, "should not generate fills"
    assert cancels == [
        sell_id1,
        sell_id2
    ], "lower priced sell should cancel previous sells"

    buy_id, fills, cancels = order_book.add_order(
        Side.BUY,
        Decimal('10'),
        5,
        Style.IMMEDIATE_OR_CANCEL
    )
    assert buy_id is not None, "should generate order"
    assert fills == [
        Fill(buy_id, sell_id3, Decimal('10'), 5)
    ]
    assert cancels == [sell_id3], "should cancel the partially unfilled sell"

    assert str(order_book) == ' : ', "the order book should be empty"

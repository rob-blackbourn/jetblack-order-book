"""Tests for book-or-cancel orders"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side, Style


def test_book_or_cancel_passive():
    """Test a book-or-cancel where the order is passive"""
    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    buy_id, _, _ = order_book.add_order(
        Side.BUY,
        Decimal('11'),
        5,
        Style.BOOK_OR_CANCEL
    )
    sell_id, fills, cancels = order_book.add_order(
        Side.SELL,
        Decimal('11'),
        5,
        Style.LIMIT
    )

    assert buy_id is not None and sell_id is not None and fills == [
        Fill(buy_id, sell_id, Decimal('11'), 5)
    ], "successful fill"
    assert not cancels, "should be no cancels"

    assert str(order_book) == " : "


def test_book_or_cancel_aggressor():
    """Test a book-or-cancel where the order is the aggressor"""
    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    buy_id, _, _ = order_book.add_order(
        Side.BUY,
        Decimal('11'),
        5,
        Style.LIMIT
    )
    assert buy_id is not None

    sell_id, fills, cancels = order_book.add_order(
        Side.SELL,
        Decimal('11'),
        5,
        Style.BOOK_OR_CANCEL
    )
    assert sell_id is not None

    assert not fills, "should not fill"
    assert cancels == [sell_id], "should cancel the sell"

    assert str(order_book) == "11x5 : "

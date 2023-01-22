"""Tests for fill-or-kill orders"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side, Style


def test_fill_of_kill_buy():
    """Test a successful kill or fill where the order was a buy"""
    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    order_book.add_limit_order(Side.BUY, Decimal('10'), 5, Style.LIMIT)
    buy_id, _, _ = order_book.add_limit_order(
        Side.BUY,
        Decimal('11'),
        5,
        Style.FILL_OR_KILL
    )
    sell_id, fills, cancels = order_book.add_limit_order(
        Side.SELL,
        Decimal('11'),
        15,
        Style.LIMIT
    )

    assert buy_id is not None and sell_id is not None and fills == [
        Fill(buy_id, sell_id, Decimal('11'), 5)
    ], "successful fill"
    assert not cancels, "should be no cancels"

    assert str(order_book) == "10x5 : 11x10"

    sell_id, fills, cancels = order_book.add_limit_order(
        Side.BUY,
        Decimal('11'),
        15,
        Style.FILL_OR_KILL
    )

    assert not fills, "should be no fills"
    assert cancels == [sell_id], "fill-or-kill should be cancelled"


def test_fill_or_kill_sell():
    """Test a successful kill or fill where the order was a sell"""
    order_book = OrderBook()

    order_book.add_limit_order(Side.SELL, Decimal('11'), 5, Style.LIMIT)
    sell_id, _, _ = order_book.add_limit_order(
        Side.SELL,
        Decimal('10'),
        5,
        Style.FILL_OR_KILL
    )
    buy_id, fills, cancels = order_book.add_limit_order(
        Side.BUY,
        Decimal('10'),
        15,
        Style.LIMIT
    )

    assert buy_id is not None and sell_id is not None and fills == [
        Fill(buy_id, sell_id, Decimal('10'), 5)
    ], "successful fill"
    assert not cancels, "there should be no cancels"

    assert str(order_book) == "10x10 : 11x5"

    sell_id, fills, cancels = order_book.add_limit_order(
        Side.SELL,
        Decimal('10'),
        15,
        Style.FILL_OR_KILL
    )

    assert not fills, "should not fill"
    assert cancels == [sell_id], "should cancel order"


def test_fill_or_kill_cancel_buy_order():
    """Should cancel buys in time order"""

    order_book = OrderBook()

    buy_id1, _, _ = order_book.add_limit_order(
        Side.BUY,
        Decimal('11'),
        10,
        Style.FILL_OR_KILL
    )
    buy_id2, _, _ = order_book.add_limit_order(
        Side.BUY,
        Decimal('11'),
        10,
        Style.FILL_OR_KILL
    )
    _, fills, cancels = order_book.add_limit_order(
        Side.SELL,
        Decimal('10'),
        5,
        Style.LIMIT
    )

    assert not fills, "should not fill"
    assert cancels == [buy_id1, buy_id2], "should cancel in order"


def test_fill_or_kill_cancel_sell_order():
    """Should cancel sells in time order"""

    order_book = OrderBook()

    sell_id1, _, _ = order_book.add_limit_order(
        Side.SELL,
        Decimal('10'),
        10,
        Style.FILL_OR_KILL
    )
    sell_id2, _, _ = order_book.add_limit_order(
        Side.SELL,
        Decimal('10'),
        10,
        Style.FILL_OR_KILL
    )
    _, fills, cancels = order_book.add_limit_order(
        Side.BUY,
        Decimal('11'),
        5,
        Style.LIMIT
    )

    assert not fills, "should not fill"
    assert cancels == [sell_id1, sell_id2], "should cancel in order"

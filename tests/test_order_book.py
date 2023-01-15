"""Tests for the order book"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, LimitOrder, Side


def test_order_book():
    order_book = OrderBook()

    assert str(order_book) == ' : '

    order_id, fills = order_book.add_limit_order(Side.BUY, Decimal('10.5'), 10)
    assert order_id == 1
    assert len(fills) == 0
    assert str(order_book) == '10.5x10 : '

    order_id, fills = order_book.add_limit_order(
        Side.SELL, Decimal('10.5'), 10
    )
    assert order_id == 2
    assert len(fills) == 1
    assert fills == [Fill(1, 2, Decimal('10.5'), 10)]
    assert str(order_book) == ' : '

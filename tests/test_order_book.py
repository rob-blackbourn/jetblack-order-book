"""Tests for the order book"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side


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


def test_smoke():
    order_book = OrderBook()

    order_book.add_limit_order(Side.BUY, Decimal('10.0'), 10)
    order_book.add_limit_order(Side.BUY, Decimal('10.5'), 5)
    order_book.add_limit_order(Side.BUY, Decimal('10.0'), 20)
    order_book.add_limit_order(Side.BUY, Decimal('9.5'), 30)
    order_book.add_limit_order(Side.SELL, Decimal('11.5'), 15)
    order_book.add_limit_order(Side.SELL, Decimal('11.0'), 10)
    order_book.add_limit_order(Side.SELL, Decimal('12.0'), 20)
    order_book.add_limit_order(Side.SELL, Decimal('13.5'), 30)

    assert str(
        order_book
    ) == '9.5x30,10.0x30,10.5x5 : 11.0x10,11.5x15,12.0x20,13.5x30'

    order_book.add_limit_order(Side.SELL, Decimal('10.5'), 15)

    assert str(
        order_book
    ) == '9.5x30,10.0x30 : 10.5x10,11.0x10,11.5x15,12.0x20,13.5x30'

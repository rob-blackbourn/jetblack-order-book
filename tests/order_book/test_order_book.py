"""Tests for the order book"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Side, Style


def test_smoke():
    """
    A test exercising many features.
    """
    order_book = OrderBook()

    # Build up the book
    order_book.add_limit_order(Side.BUY, Decimal('10.0'), 10, Style.VANILLA)
    order_book.add_limit_order(Side.BUY, Decimal('10.5'), 5, Style.VANILLA)
    order_book.add_limit_order(Side.BUY, Decimal('10.0'), 20, Style.VANILLA)
    order_book.add_limit_order(Side.BUY, Decimal('9.5'), 30, Style.VANILLA)
    order_book.add_limit_order(Side.SELL, Decimal('11.5'), 15, Style.VANILLA)
    order_book.add_limit_order(Side.SELL, Decimal('11.0'), 10, Style.VANILLA)
    order_book.add_limit_order(Side.SELL, Decimal('12.0'), 20, Style.VANILLA)
    order_book.add_limit_order(Side.SELL, Decimal('13.5'), 30, Style.VANILLA)

    assert str(
        order_book
    ) == '9.5x30,10.0x30,10.5x5 : 11.0x10,11.5x15,12.0x20,13.5x30'

    _, fills, _ = order_book.add_limit_order(
        Side.SELL,
        Decimal('10.5'),
        15, Style.VANILLA
    )
    assert len(fills) == 1
    assert fills[0].size == 5
    assert str(
        order_book
    ) == '9.5x30,10.0x30 : 10.5x10,11.0x10,11.5x15,12.0x20,13.5x30'

    # Cross the book. The price should be that of the aggressor (the buy).
    _, fills, _ = order_book.add_limit_order(
        Side.BUY,
        Decimal('11.0'),
        25,
        Style.VANILLA
    )
    assert len(fills) == 2
    assert all(fill.price == Decimal('11.0') for fill in fills)
    assert str(
        order_book
    ) == '9.5x30,10.0x30,11.0x5 : 11.5x15,12.0x20,13.5x30'

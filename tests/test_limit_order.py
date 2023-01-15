"""Tests for limit orders"""

from decimal import Decimal

from jetblack_order_book import LimitOrder, Side


def test_comparison():
    order1 = LimitOrder(1, Side.BUY, Decimal('10.5'), 100)
    order2 = LimitOrder(2, Side.BUY, Decimal('10.5'), 100)

    assert order1 < order2, "lt by order_id"

    order3 = LimitOrder(3, Side.BUY, Decimal('10.5'), 100)
    order4 = LimitOrder(4, Side.SELL, Decimal('10.5'), 100)
    assert order4 < order3, "lt by side"

    order5 = LimitOrder(5, Side.SELL, Decimal('12.5'), 100)
    order6 = LimitOrder(6, Side.SELL, Decimal('10.5'), 100)
    assert order6 < order5, "lt by price"

    order5 = LimitOrder(5, Side.SELL, Decimal('10.5'), 200)
    order6 = LimitOrder(6, Side.SELL, Decimal('10.5'), 100)
    assert order6 < order5, "lt by size"

    assert not (order1 < order1), "not lt when equal"

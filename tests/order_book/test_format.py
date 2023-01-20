"""Tests for formatting"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Side, Style


def test_format():
    """Test for formatting"""
    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    # Add 3 buys and 2 sells at distinct price levels.
    order_book.add_limit_order(Side.BUY, Decimal('10.1'), 5, Style.VANILLA)
    order_book.add_limit_order(Side.BUY, Decimal('10.2'), 5, Style.VANILLA)
    order_book.add_limit_order(Side.BUY, Decimal('10.3'), 5, Style.VANILLA)

    order_book.add_limit_order(Side.SELL, Decimal('11.1'), 5, Style.VANILLA)
    order_book.add_limit_order(Side.SELL, Decimal('11.2'), 5, Style.VANILLA)

    assert str(
        order_book
    ) == '10.1x5,10.2x5,10.3x5 : 11.1x5,11.2x5', "the order book represent the orders"

    assert format(
        order_book,
        "4"
    ) == '10.1x5,10.2x5,10.3x5 : 11.1x5,11.2x5', "show all orders if the length exceeds the orders"

    assert format(
        order_book,
        "3"
    ) == '10.1x5,10.2x5,10.3x5 : 11.1x5,11.2x5', "show all orders if the length matches the orders"

    assert format(
        order_book,
        "2"
    ) == '10.2x5,10.3x5 : 11.1x5,11.2x5', "show two orders per side"

    assert format(
        order_book,
        "1"
    ) == '10.3x5 : 11.1x5', "show one order per side"

    try:
        format(order_book, "0")
        assert False, "format length should be greater than 0"
    except ValueError:
        assert True, "Format should be less than 0"

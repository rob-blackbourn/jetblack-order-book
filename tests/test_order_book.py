"""Tests for the order book"""

from decimal import Decimal

from jetblack_order_book import OrderBook, Fill, Side


def test_smoke():
    """
    A test exercising many features.
    """
    order_book = OrderBook()

    # Build up the book
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

    _, fills = order_book.add_limit_order(Side.SELL, Decimal('10.5'), 15)
    assert len(fills) == 1
    assert fills[0].size == 5
    assert str(
        order_book
    ) == '9.5x30,10.0x30 : 10.5x10,11.0x10,11.5x15,12.0x20,13.5x30'

    # Cross the book. The price should be that of the aggressor (the buy).
    _, fills = order_book.add_limit_order(Side.BUY, Decimal('11.0'), 25)
    assert len(fills) == 2
    assert all(fill.price == Decimal('11.0') for fill in fills)
    assert str(
        order_book
    ) == '9.5x30,10.0x30,11.0x5 : 11.5x15,12.0x20,13.5x30'


def test_partial_fill():
    """
    A partial fill is an order which matches less than the full amount of the
    matched order, leaving som of the matched order in the book.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : '

    buy1, _ = order_book.add_limit_order(Side.BUY, Decimal('10.5'), 10)
    sell1, fills = order_book.add_limit_order(Side.SELL, Decimal('10.5'), 5)

    assert fills == [
        Fill(buy1, sell1, Decimal('10.5'), 5)
    ]
    assert str(order_book) == '10.5x5 : '


def test_order_time_order():
    """
    Orders at the same price should be executed in the order they are received.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : '

    # Add two buy orders at the same price
    buy1, _ = order_book.add_limit_order(Side.BUY, Decimal('10.5'), 10)
    buy2, _ = order_book.add_limit_order(Side.BUY, Decimal('10.5'), 5)

    # Add a sell for the same price with a greater total size
    sell, fills = order_book.add_limit_order(
        Side.SELL, Decimal('10.5'), 20
    )

    assert fills == [
        Fill(buy1, sell, Decimal('10.5'), 10),
        Fill(buy2, sell, Decimal('10.5'), 5),
    ]

    assert str(order_book) == ' : 10.5x5'


def test_order_cross():
    """
    A cross occurs when a sell/buy order is placed at a price below/above
    the best bid/offer. In this case the price of the sell/buy is used, rather
    than the matched price.
    """
    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    buy1, _ = order_book.add_limit_order(Side.BUY, Decimal('10.5'), 5)
    buy2, _ = order_book.add_limit_order(Side.BUY, Decimal('11.0'), 10)
    sell1, fills = order_book.add_limit_order(Side.SELL, Decimal('10.0'), 15)

    assert fills == [
        Fill(buy2, sell1, Decimal('10.0'), 10),
        Fill(buy1, sell1, Decimal('10.0'), 5),
    ], "fills should have price of the sell"
    assert str(order_book) == ' : ', "the order book should be empty"


def test_order_book_amend_size():
    """
    The size of a limit order can be changed.
    """

    order_book = OrderBook()

    assert str(order_book) == ' : ', "the order book should be empty"

    _, _ = order_book.add_limit_order(Side.BUY, Decimal('10.5'), 10)
    sell2, _ = order_book.add_limit_order(Side.SELL, Decimal('10.6'), 10)

    assert str(
        order_book
    ) == '10.5x10 : 10.6x10', "the order book should represent the orders"

    order_book.amend_limit_order(sell2, 5)
    assert str(
        order_book
    ) == '10.5x10 : 10.6x5', "the order book should show the change in size"


def test_order_book_cancel_order():
    order_book = OrderBook()

    assert str(order_book) == ' : '

    # Add two buy orders at the same price
    order_book.add_limit_order(Side.BUY, Decimal('10.5'), 10)
    order_book.add_limit_order(Side.SELL, Decimal('10.6'), 10)
    sell2, _ = order_book.add_limit_order(Side.SELL, Decimal('10.6'), 5)

    assert str(
        order_book
    ) == '10.5x10 : 10.6x15'

    order_book.cancel_limit_order(sell2)
    assert str(
        order_book
    ) == '10.5x10 : 10.6x10'

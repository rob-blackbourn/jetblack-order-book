"""Tests for the exchange order book"""

from decimal import Decimal

from jetblack_order_book import ExchangeOrderBook, Side


def test_exchange_order_book_smoke():
    order_book = ExchangeOrderBook(["AAPL", "MSFT"])

    orders = [
        ('AAPL', Side.BUY, Decimal('134.76'), 10),
        ('MSFT', Side.BUY, Decimal('239.23'), 5),
        ('MSFT', Side.SELL, Decimal('239.28'), 15),
        ('MSFT', Side.SELL, Decimal('239.30'), 2),
        ('AAPL', Side.BUY, Decimal('134.72'), 50),
        ('MSFT', Side.BUY, Decimal('239.14'), 20),
        ('MSFT', Side.BUY, Decimal('239.12'), 25),
        ('MSFT', Side.BUY, Decimal('239.14'), 10),
        ('AAPL', Side.SELL, Decimal('134.79'), 25),
        ('AAPL', Side.SELL, Decimal('135.00'), 40),
        ('AAPL', Side.SELL, Decimal('135.05'), 100),
        ('MSFT', Side.SELL, Decimal('239.32'), 80),
        ('AAPL', Side.SELL, Decimal('135.08'), 50),
        ('AAPL', Side.BUY, Decimal('134.20'), 120),
    ]
    for ticker, side, price, size in orders:
        order_book.add_limit_order(ticker, side, price, size)

    assert str(
        order_book.books['AAPL']
    ) == '134.20x120,134.72x50,134.76x10 : 134.79x25,135.00x40,135.05x100,135.08x50'

    assert str(
        order_book.books['MSFT']
    ) == '239.12x25,239.14x30,239.23x5 : 239.28x15,239.30x2,239.32x80'

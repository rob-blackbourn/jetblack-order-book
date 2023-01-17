# jetblack-order-book

This is a demonstration implementation of an algorithm for a time weighted limit order book
written in Python.

A limit order is an order that can be filled at a given price.

The orders are "time weighted", in that older orders are executed before newer orders, where the prices are the same.

## Implementation

At the base layer there is a `LimitOrder` which holds the `order_id`, `side`, `price` and `size` of an order.

As multiple orders can be placed at the same price, each price holds an `AggregateOrder` which contains a queue of all the individual orders.
As the orders are executed in the sequence in which they were placed (FIFO), new orders are appended to the back of the queue,
and order to execute are taken from the front of the queue.

The aggregated orders are arranged by price by the `AggregatedOrderSide` class.
This arranges the aggregated orders by price ascending, so the best bid is the last
aggregated order, and the best offer is the first aggregated order.

The aggregated order sides are brought together in the `OrderBook`, which manages
the orders and performs *matching* to produce fills when an order matches or crosses.
Crossing is a special case where an order for a buy (or sell) is made at a higher (or lower) price than the best offer (or bid).

Finally there is an `ExchangeOrderBook` which maintains the order books
for a given set of tickers.

## Usage

The following is taken from the tests.

```python
from decimal import Decimal
from jetblack_order_book import ExchangeOrderBook, Side, Fill

# Create and exchange order book for two tickers.
order_book = ExchangeOrderBook(["AAPL", "MSFT"])

# Build the book.
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

# Submit a matching order.
order_id, fills = order_book.add_limit_order(
    'AAPL',
    Side.BUY,
    Decimal('134.79'),
    20
)
assert len(fills) == 1
assert fills == [
    Fill(8, 3, Decimal('134.79'), 20)
]
```

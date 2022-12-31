"""Main"""

from pathlib import Path
from typing import Optional

from order_book.messages import iter_messages
from order_book.orders import iter_order_book, OrderBook


def process(messages_path: Path, order_book_path: Path, levels: int) -> None:
    message_feed = iter_messages(messages_path)
    order_book_feed = iter_order_book(order_book_path, levels)
    next_order_book: Optional[OrderBook] = None

    # Discard the first message
    next(message_feed)

    while True:
        try:
            order_book = next(order_book_feed)

            if next_order_book and order_book != next_order_book:
                raise Exception("Match error")

            message = next(message_feed)
            next_order_book = order_book.process(message)

        except StopIteration:
            break


def display(messages_path: Path, order_book_path: Path, levels: int) -> None:
    message_feed = iter_messages(messages_path)
    order_book_feed = iter_order_book(order_book_path, levels)

    # Discard the first message
    next(message_feed)

    while True:
        try:
            order_book = next(order_book_feed)
            print(order_book)
            message = next(message_feed)
            print(message)

        except StopIteration:
            break


if __name__ == '__main__':
    LEVELS = 5
    SYMBOL = 'AAPL'
    process(
        Path(f"data/{SYMBOL}_2012-06-21_34200000_57600000_message_{LEVELS}.csv"),
        Path(f"data/{SYMBOL}_2012-06-21_34200000_57600000_orderbook_{LEVELS}.csv"),
        LEVELS
    )

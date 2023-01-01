"""Main"""

from pathlib import Path
from typing import Optional

from jetblack_order_book.order_book import OrderBook
from jetblack_order_book.readers import iter_order_book, iter_messages


def process(messages_path: Path, order_book_path: Path, levels: int) -> None:
    message_feed = iter_messages(messages_path)
    order_book_feed = iter_order_book(order_book_path, levels)
    next_order_book: Optional[OrderBook] = None

    # Discard the first message
    next(message_feed)

    count = 0
    while True:
        try:
            order_book = next(order_book_feed)
            print(order_book)

            if next_order_book is None:
                next_order_book = order_book
            elif order_book != next_order_book:
                raise Exception("Match error")

            message = next(message_feed)
            print(message)

            next_order_book = next_order_book.process(message)
            print(format(next_order_book, str(levels)))
            print(next_order_book)

            count += 1
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

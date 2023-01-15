"""Exchange Order Book"""

from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Tuple

from .fill import Fill
from .order_book import OrderBook
from .order_types import Side


class ExchangeOrderBook:

    def __init__(self) -> None:
        self.order_books: Dict[str, OrderBook] = defaultdict(OrderBook)

    def add_limit_order(
            self,
            ticker: str,
            side: Side,
            price: Decimal,
            size: int
    ) -> Tuple[int, List[Fill]]:
        order_book = self.order_books[ticker]
        return order_book.add_limit_order(side, price, size)

    def amend_limit_order(self, ticker: str, order_id: int, size: int) -> None:
        order_book = self.order_books[ticker]
        order_book.amend_limit_order(order_id, size)

    def cancel_limit_order(self, ticker: str, order_id: int) -> None:
        order_book = self.order_books[ticker]
        order_book.cancel_limit_order(order_id)

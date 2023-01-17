"""Exchange Order Book"""

from decimal import Decimal
from typing import Dict, Iterable, List, Tuple

from .fill import Fill
from .limit_order import Side, Style
from .order_book import OrderBook


class ExchangeOrderBook:
    """An order book for an exchange.

    This maintains the order book for each ticker.
    """

    def __init__(self, tickers: Iterable[str]) -> None:
        """Initialise the exchange order book.

        Args:
            tickers (Iterable[str]): The tickers for which order books are kept.
        """
        self.books: Dict[str, OrderBook] = {
            ticker: OrderBook()
            for ticker in tickers
        }

    def add_limit_order(
            self,
            ticker: str,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[int, List[Fill]]:
        """Add a limit order for a ticker.

        Args:
            ticker (str): The ticker.
            side (Side): Buy or sell.
            price (Decimal): The price at which the order should be executed.
            size (int): The size of the order.
            style (Style): The order style.

        Returns:
            Tuple[int, List[Fill]]: The id of the order and any fills that
            were generated.
        """
        order_book = self.books[ticker]
        return order_book.add_limit_order(side, price, size, style)

    def amend_limit_order(self, ticker: str, order_id: int, size: int) -> None:
        """Amend a limit order.

        Args:
            ticker (str): The ticker.
            order_id (int): The id of the order.
            size (int): The new size.
        """
        order_book = self.books[ticker]
        order_book.amend_limit_order(order_id, size)

    def cancel_limit_order(self, ticker: str, order_id: int) -> None:
        """Cancel a limit order.

        Args:
            ticker (str): The ticker.
            order_id (int): The order id.
        """
        order_book = self.books[ticker]
        order_book.cancel_limit_order(order_id)

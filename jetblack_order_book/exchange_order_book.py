"""Exchange Order Book"""

from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .abstract_types import PluginFactory
from .constants import ALL_PLUGINS
from .fill import Fill
from .order import Side, Style
from .order_book import OrderBook


class ExchangeOrderBook:
    """An order book for an exchange.

    This maintains the order book for each ticker.
    """

    def __init__(
            self,
            tickers: Iterable[str],
            plugins: Sequence[PluginFactory] = ALL_PLUGINS
    ) -> None:
        """Initialise the exchange order book.

        Args:
            tickers (Iterable[str]): The tickers for which order books are kept.
            plugins (Sequence[PluginFactory], Optional): The plugins. Defaults
                to `ALL_PLUGINS`.
        """
        self.books: Dict[str, OrderBook] = {
            ticker: OrderBook(plugins)
            for ticker in tickers
        }

    def add_order(
            self,
            ticker: str,
            side: Side,
            price: Decimal,
            size: int,
            style: Style
    ) -> Tuple[Optional[int], List[Fill], List[int]]:
        """Add an order for a ticker.

        Args:
            ticker (str): The ticker.
            side (Side): Buy or sell.
            price (Decimal): The price at which the order should be executed.
            size (int): The size of the order.
            style (Style): The order style.

        Returns:
            Tuple[Optional[int], List[Fill], List[int]]: The id of the order (if
            an order could be created), any fills that were generated, and a
            list of cancelled order ids.
        """
        order_book = self.books[ticker]
        return order_book.add_order(side, price, size, style)

    def amend_order(self, ticker: str, order_id: int, size: int) -> None:
        """Amend aa order.

        Args:
            ticker (str): The ticker.
            order_id (int): The id of the order.
            size (int): The new size.
        """
        order_book = self.books[ticker]
        order_book.amend_order(order_id, size)

    def cancel_order(self, ticker: str, order_id: int) -> None:
        """Cancel an order.

        Args:
            ticker (str): The ticker.
            order_id (int): The order id.
        """
        order_book = self.books[ticker]
        order_book.cancel_order(order_id)

"""Constants"""

from .plugins import (
    create_book_or_cancel_plugin,
    create_fill_or_kill_plugin,
    create_immediate_or_cancel_plugin
)

ALL_PLUGINS = (
    create_book_or_cancel_plugin,
    create_fill_or_kill_plugin,
    create_immediate_or_cancel_plugin
)

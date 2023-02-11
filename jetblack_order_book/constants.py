"""Constants"""

from typing import Sequence

from .plugins import (
    BookOrCancelPlugin,
    FillOrKillPlugin,
    ImmediateOrCancelPlugin
)

from .abstract_types import PluginFactory

ALL_PLUGINS: Sequence[PluginFactory] = (
    BookOrCancelPlugin,
    FillOrKillPlugin,
    ImmediateOrCancelPlugin
)

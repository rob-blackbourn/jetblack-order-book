"""Types"""

from enum import IntEnum


class EventType(IntEnum):
    SUBMIT = 1  # Submission of a new limit order
    CANCEL = 2  # Cancellation (partial deletion of a limit order)
    DELETE = 3  # Deletion (total deletion of a limit order)
    EXECUTE_VISIBLE = 4  # Execution of a visible limit order
    EXECUTE_HIDDEN = 5  # Execution of a hidden limit order
    CROSS = 6  # Indicates a cross trade, e.g. auction trade
    HALT = 7  # Trading halt indicator (detailed information below)


class Side(IntEnum):
    BUY = 1
    SELL = -1

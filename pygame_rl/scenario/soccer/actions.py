# Native modules
from enum import IntEnum


class Actions(IntEnum):
    # Indicates that rule-based AI will override the action
    NOOP = 0
    MOVE_RIGHT = 1
    MOVE_UP = 2
    MOVE_LEFT = 3
    MOVE_DOWN = 4
    STAND = 5

"""Provides useful CLI utilities for more efficient displaying of information.
"""
from typing import Any, Tuple
from enum import Enum

import curses


class ColorPair(Enum):
    STANDARD = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4

    TITLE = 5
    SELECTED = 6

    @classmethod
    def init_color_pairs(cls) -> None:
        """Initialize color pairs.
        """
        curses.init_pair(ColorPair.STANDARD.value, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.SUCCESS.value, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.WARNING.value, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.ERROR.value, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.TITLE.value, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.SELECTED.value, curses.COLOR_WHITE, curses.COLOR_BLUE)

    @property
    def pair(self) -> Any:
        """Return the color pair represented by the item.
        """
        return curses.color_pair(self.value)


class Anchor(Enum):
    TOP_LEFT = (0, 0)
    TOP_CENTER = (0, 1)
    TOP_RIGHT = (0, 2)
    CENTER_LEFT = (1, 0)
    CENTER_CENTER = (1, 1)
    CENTER_RIGHT = (1, 2)
    BOTTOM_LEFT = (2, 0)
    BOTTOM_CENTER = (2, 1)
    BOTTOM_RIGHT = (2, 2)

    def offset(self, lines: int, max_line: int) -> Tuple[int, int]:
        """Return the offset required to position the given <lines> with a given <max_line> in the correct
        positioning for the anchor.
        """
        y_offset = -int(lines * self.value[0] / 2)
        x_offset = -int(max_line * self.value[1] / 2)
        return y_offset, x_offset

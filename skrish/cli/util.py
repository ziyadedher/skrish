"""Provides useful CLI utilities for more efficient displaying of information.
"""
from typing import Any
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
"""Provides useful CLI utilities for more efficient displaying of information.
"""
from typing import Tuple, Any
from enum import Enum

import curses


class ColorPair(Enum):
    STANDARD = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4

    TITLE = 5

    @classmethod
    def init_color_pairs(cls) -> None:
        """Initialize color pairs.
        """
        curses.init_pair(ColorPair.STANDARD.value, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.SUCCESS.value, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.WARNING.value, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.ERROR.value, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.TITLE.value, curses.COLOR_RED, curses.COLOR_BLACK)

    @property
    def pair(self) -> Any:
        """Return the color pair represented by the item.
        """
        return curses.color_pair(self.value)


def centeryx(stdscr, message: str, vertical=True, horizontal=True) -> Tuple[int, int]:
    """Return the y and x parameters required to center the given <message> in the given <screen>.
    """
    return positionyx(stdscr, message,
                      0.5 if vertical else None,
                      0.5 if horizontal else None)


def positionyx(stdscr, message: str, vertical=None, horizontal=None) -> Tuple[int, int]:
    """Return the y and x parameters required to position the given <message> at the given percentages of the screen.
    """
    message_array = message.split("\n")
    message_length = max(len(line) for line in message_array)
    y_max, x_max = stdscr.getmaxyx()
    y, x = stdscr.getyx()

    y_start, x_start = y, x
    if vertical:
        y_start = int((y_max - len(message_array) - 1) * vertical)
    if horizontal:
        x_start = int((x_max - message_length) * horizontal)

    return y_start, x_start
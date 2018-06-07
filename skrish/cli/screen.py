"""Manages a screen wrapper class around the default curses window.
"""
import time
from typing import Optional

from skrish.cli import util


class Screen:
    """Wrapper class for curses default window to provide extra functionality.
    """

    def __init__(self, stdscr) -> None:
        """Initialize this screen with the given ncurses window.
        """
        self.screen = stdscr

        # Forward basic functionality
        self.clear = self.screen.clear
        self.refresh = self.screen.refresh
        self.getkey = self.screen.getkey
        self.getch = self.screen.getch
        self.border = self.screen.border
        self.keypad = self.screen.keypad
        self.getyx = self.screen.getyx
        self.getmaxyx = self.screen.getmaxyx
        self.nodelay = self.screen.nodelay

    def display(self, message: str, y: Optional[int] = None, x: Optional[int] = None, *args) -> None:
        """Print lines to screen in correct formatting at the given <y> and <x> if specified.
        """
        message_array = message.split("\n")
        offset = 0

        for line in message_array:
            if line == "":
                line = "\n"

            cursor_y, cursor_x = self.screen.getyx()
            self.screen.addstr((y if y else cursor_y) + offset,
                               x if x else cursor_x,
                               line, *args)
            offset += 1

    def scroll_message(self, message: str, speed: int,
                       y_start: int, x_start: int, y_end: int, x_end: int,
                       *args, skippable=False) -> None:
        """Scroll the given <message> from <y_start>, <x_start> to <y_end>, <x_end> where the end's must be greater
        than or equal to the respective starts.
        """
        # TODO: implement vertical scrolling

        self.screen.nodelay(True)

        cur_y, cur_x = y_start, x_start
        while cur_y < y_end or cur_x < x_end:
            if skippable and self.screen.getch() > 0:
                break

            start_time = time.time()

            y, x, new_message = cur_y, cur_x, message
            if x < 1:
                new_message = "\n".join(line[-int(x):] for line in message.split("\n"))
                x = 1

            anti_clear = " " + "\n ".join(new_message.split("\n"))  # Adding a space to not need to clear screen
            self.display(anti_clear,
                         round(y), round(x),
                         *args)
            self.refresh()

            deltatime = time.time() - start_time
            change = speed * deltatime

            if cur_y + change <= y_end:
                cur_y += change
            else:
                cur_y = y_end

            if cur_x + change <= x_end:
                cur_x += change
            else:
                cur_x = x_end

        self.screen.nodelay(False)


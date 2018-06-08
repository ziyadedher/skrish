"""Manages a screen wrapper class around the default curses window.
"""
import time
from typing import Optional, Tuple


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

    def display(self, message: str, y: Optional[int] = None, x: Optional[int] = None, *args,
                refresh: bool = True) -> None:
        """Print lines to screen in correct formatting at the given <y> and <x> if specified.
        """
        message_list = message.strip("\n").split("\n")
        offset = 0

        for line in message_list:
            cursor_y, cursor_x = self.screen.getyx()
            self.screen.addstr((y if y is not None else cursor_y) + offset,
                               x if x is not None else cursor_x,
                               line, *args)
            offset += 1

        if refresh:
            self.screen.refresh()

    # FIXME: crashes when diagonal from out-of-screen to out-of-screen
    def scroll_message(self, message: str, seconds: float,
                       y_start: int, x_start: int, y_end: int, x_end: int,
                       *args, skippable=False) -> None:
        """Scroll the given <message> from <y_start>, <x_start> to <y_end>, <x_end> in the given <seconds>.
        """
        message_list = message.strip("\n").split("\n")
        y_max, x_max = self.getmaxyx()

        # To offset the anti-clear padding
        y_start -= 1
        x_start -= 1
        y_end -= 1
        x_end -= 1

        if skippable:
            self.screen.nodelay(True)

        i = 0
        last_time = time.time()
        while i < 1:
            if skippable and self.screen.getch() > 0:
                self.clear()
                i = 1

            # Manage timing
            cur_time = time.time()
            deltatime, last_time = cur_time - last_time, cur_time
            i += deltatime / seconds
            if i > 1:
                i = 1

            # Interpolate between the two points
            cur_y = (y_start * (1 - i)) + (y_end * i)
            cur_x = (x_start * (1 - i)) + (x_end * i)

            lines = len(message_list)
            max_line = max(len(line) for line in message_list) if message_list else 0

            # If the message is out of bounds, then cut it off to prevent an error and choose padding
            left_free, right_free, top_free, bottom_free = True, True, True, True
            y, x, new_message_list = cur_y, cur_x, message_list
            if x < 0:
                new_message_list = [line[-round(x):] for line in new_message_list]
                left_free = False
                x = 0
            if x + max_line + 2 > x_max:
                if x >= x_max - 1:
                    x = x_max - 1
                new_message_list = [line[:x_max - round(x) - 1] for line in new_message_list]
                right_free = False
            if y < 0:
                new_message_list = new_message_list[-round(y):]
                top_free = False
                y = 0
            if y + lines + 2 > y_max:
                if y >= y_max - 1:
                    y = y_max - 1
                new_message_list = new_message_list[:y_max - round(y) - 1]
                bottom_free = False

            # Pad the message with spaces to not need to clear
            h_padding, v_padding = " ", (" " * max_line)
            anti_clear_list = [(h_padding * left_free + line + h_padding * right_free) for line in new_message_list]
            anti_clear = top_free * (v_padding + "\n") + ("\n".join(anti_clear_list)) + ("\n" + v_padding) * bottom_free

            self.display(anti_clear, round(y), round(x), *args)

        if skippable:
            self.screen.nodelay(False)

    def positionyx(self, message: str, vertical=None, horizontal=None) -> Tuple[int, int]:
        """Return the y and x parameters required to position the given <message> at the given percentages of the screen.
        """
        message_array = message.strip("\n").split("\n")
        y_max, x_max = self.getmaxyx()
        y, x = self.getyx()

        y_start, x_start = y, x
        if vertical:
            y_start = int((y_max - len(message_array)) * vertical)
        if horizontal:
            x_start = int((x_max - max(len(line) for line in message_array)) * horizontal)

        return y_start, x_start


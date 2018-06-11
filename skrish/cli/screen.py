"""Manages a screen wrapper class around the default curses window.
"""
import time
from typing import Optional, Tuple, List, Union

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
        self.box = self.screen.box
        self.keypad = self.screen.keypad
        self.getyx = self.screen.getyx
        self.getmaxyx = self.screen.getmaxyx
        self.nodelay = self.screen.nodelay
        self.derwin = self.screen.derwin

    def put(self, message: str, vertical: Optional[float] = None, horizontal: Optional[float] = None, *args,
            refresh: bool = True, anchor: util.Anchor = util.Anchor.CENTER_CENTER,
            offset: Tuple[int, int] = (0, 0)) -> None:
        """Print lines to screen in correct formatting at the given <y> and <x> percentages of the screen
        if specified, and with <anchor> if specified. Accepts an integer absolute <offset> off the given percentages.
        Also passes in all other <args> to the `addstr`.

        If the <y> or <x> positions are not specified, the text will be placed at the cursor position for the
        respective axis or axes not specified.

        The anchor is the position of the text to place at the given percentages.

        NOTE: Try not to use the offset parameter unless necessary.
        """
        message_list = message.strip("\n").split("\n")
        if vertical is None:
            vertical = self._absolute_to_scale(*self.getyx)[0]
        if horizontal is None:
            horizontal = self._absolute_to_scale(*self.getyx)[1]

        y_max, x_max = self.getmaxyx()
        y, x = self._position_message(message_list, anchor, vertical, horizontal)

        num_lines = len(message_list)
        max_line = max(len(line) for line in message_list)
        counter = 0

        # If the message is out of bounds, then cut it off to prevent an error
        # FIXME: manual offset is not accounted for
        # FIXME: moving out of bottom-right corner crashes
        new_message_list = message_list
        if y < 0:
            new_message_list = message_list[-y:]
            y = 0
        if y + num_lines > y_max:
            if y > y_max:
                y = y_max
            new_message_list = message_list[:y_max - y]

        if x < 0:
            new_message_list = [line[-x:] for line in new_message_list]
            x = 0
        if x + max_line > x_max:
            if x > x_max:
                x = x_max
            new_message_list = [line[:x_max - x] for line in new_message_list]

        for line in new_message_list:
            if not line:
                continue

            cursor_y, cursor_x = self.screen.getyx()

            self.screen.addstr((y if y is not None else cursor_y) + counter + offset[0],
                               (x if x is not None else cursor_x) + offset[1],
                               line, *args)
            counter += 1

        if refresh:
            self.screen.refresh()

    def scroll_message(self, message: str, seconds: float,
                       vertical_start: float, horizontal_start: float, vertical_end: float, horizontal_end: float,
                       *args, anchor: util.Anchor = util.Anchor.CENTER_CENTER, skippable: bool = False) -> None:
        """Scroll the given <message> from <vertical_start>, <horizontal_start> to <vertical_end>, <horizontal_end>
        percentages of the screen in the given <seconds> with the message latched to the given <anchor>.
        If <skippable> is set, then any key will skip the transition. Also passes in all other <args> to the `addstr`.
        """
        message_list = message.strip("\n").split("\n")

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
            cur_vertical = (vertical_start * (1 - i)) + (vertical_end * i)
            cur_horizontal = (horizontal_start * (1 - i)) + (horizontal_end * i)

            # Pad the message with spaces to not need to clear
            h_padding, v_padding = " ", (" " * max(len(line) for line in message_list) if message_list else 0)
            anti_clear_list = [(h_padding + line + h_padding) for line in message_list]
            anti_clear = (v_padding + "\n") + ("\n".join(anti_clear_list)) + ("\n" + v_padding)

            self.put(anti_clear, cur_vertical, cur_horizontal, *args, anchor=anchor)

        if skippable:
            self.screen.nodelay(False)

    def _absolute_to_scale(self, y: int, x: int) -> Tuple[float, float]:
        """Convert from the absolute <y> and <x> relative to this screen to a scale percentage of the screen.
        """
        y_max, x_max = self.getmaxyx()
        return y / y_max, x / x_max

    def _position_message(self, message: Union[List[str], str], anchor: util.Anchor,
                          vertical: float, horizontal: float) -> Tuple[int, int]:
        """Return the y and x parameters required to position the given <message_list> at the given <y> and <x>
        percentages of the screen with the given <anchor>.
        """
        if isinstance(message, str):
            message = message.strip("\n").split("\n")

        y_max, x_max = self.getmaxyx()
        y_offset, x_offset = anchor.offset(message)

        y = int(vertical * y_max + y_offset)
        x = int(horizontal * x_max + x_offset)
        return y, x

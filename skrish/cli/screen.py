"""Manages a screen wrapper class around the default curses window.
"""
from typing import Tuple, List, Union, Callable, Any

from skrish.cli.util import Anchor


class Screen:
    """Wrapper class for curses default window to provide extra functionality.
    """

    def __init__(self, stdscr) -> None:
        """Initialize this screen with the given ncurses window.
        """
        self.stdscr = stdscr

        # Forward basic functionality
        self.clear = self.stdscr.clear
        self.box = self.stdscr.box

    # def grid_screen(self, dimensions_list: List[Tuple[float, float, float, float]]) -> List['Screen']:
    #     """Generates a grid of sub-screens based off the given <dimensions_list>, and returns the list of created
    #     sub-screens.
    #     """
    #     y_max, x_max = self.stdscr.getmaxyx()
    #     screens = []
    #     for dimensions in dimensions_list:
    #         y_size, x_size = y_max * dimensions[0], x_max * dimensions[1]
    #         y_offset, x_offset = y_max * dimensions[2], x_max * dimensions[3]
    #
    #         # Counteract truncating off the edge, cannot round because it is inconsistent (even-odd).
    #         if y_size + y_offset == y_max:
    #             if int(y_size) < y_size:
    #                 y_size += 1
    #         if x_size + x_offset == x_max:
    #             if int(x_size) < x_size:
    #                 x_size += 1
    #
    #         screens.append(Screen(self.stdscr.derwin(
    #             int(y_size), int(x_size),
    #             int(y_offset), int(x_offset)
    #         )))
    #     return screens

    def dialogue(self, vertical_size: float, horizontal_size: float, vertical_offset: float, horizontal_offset: float,
                 anchor: Anchor = Anchor.CENTER_CENTER) -> 'Screen':
        """Generates a dialogue box sub-screen based off the given <dimensions>, and returns the sub-screen.
        """
        y_max, x_max = self.stdscr.getmaxyx()
        y_size, x_size = y_max * vertical_size, x_max * horizontal_size
        y_anchor_offset, x_anchor_offset = anchor.offset(y_size, x_size)
        y_offset, x_offset = y_max * vertical_offset + y_anchor_offset, x_max * horizontal_offset + x_anchor_offset

        # Counteract truncating off the edge, cannot round because it is inconsistent (even-odd).
        if y_size + y_offset == y_max:
            if int(y_size) < y_size:
                y_size += 1
        if x_size + x_offset == x_max:
            if int(x_size) < x_size:
                x_size += 1

        screen = Screen(self.stdscr.derwin(
            int(y_size), int(x_size), int(y_offset), int(x_offset)
        ))

        screen.clear()
        screen.box()
        screen.stdscr.refresh()

        return screen

    def watch_keys(self, options: List[Tuple[str, List[int], str, Callable[[], Any], bool]] = None,
                   listener_screen: 'Screen' = None, vertical: float = 0.95, horizontal: float = 0.5,
                   joiner: str = "    ", show_keys: bool = True,
                   anchor: Anchor = Anchor.CENTER_CENTER, offset: Tuple[int, int] = (0, 0),
                   callback: Callable[[int], Any] = lambda i: None) -> Callable[[], Any]:
        """Watch the keys given by <options> which describes a list of tuples of the form
        ("key name", keycode, "action name", action, is_scene_switch)) on the given <listener_screen> if specified,
        otherwise it will listen on this screen. These keys will be displayed at <vertical> and <horizontal> percentages
        of the screen with the given <anchor> and <offset> and joined by <joiner> if <show_keys> is set,
        includes a <callback> for each poll of the keys that passes through the key pressed.

        Returns the final call from this watch keys to prevent further and further recursion.
        """
        if options is None:
            options = []
        if listener_screen is None:
            listener_screen = self

        # if show_keys:
        #     text_array = []
        #     for option in options:
        #         text_array.append("[{}] {}".format(option[0], option[2]))
        #
        #     text = joiner.join(text_array)
        #     self.put(text, vertical, horizontal, anchor=anchor, offset=offset)

        listener_screen.stdscr.nodelay(True)
        while True:
            key = listener_screen.stdscr.getch()
            callback(key)

            for option in options:
                if key in option[1]:
                    listener_screen.stdscr.nodelay(False)
                    call = option[3]
                    if option[4]:
                        return call

                    call = call()
                    if call is not None:
                        return call

    def absolute_to_scale(self, y: int, x: int) -> Tuple[float, float]:
        """Convert from the absolute <y> and <x> relative to this screen to a scale percentage of the screen.
        """
        y_max, x_max = self.stdscr.getmaxyx()
        return y / y_max, x / x_max

    def position_message(self, message: Union[List[str], str], anchor: Anchor,
                         vertical: float, horizontal: float) -> Tuple[int, int]:
        """Return the y and x parameters required to position the given <message_list> at the given <y> and <x>
        percentages of the screen with the given <anchor>.
        """
        if isinstance(message, str):
            message = message.strip("\n").split("\n")

        y_max, x_max = self.stdscr.getmaxyx()
        y_offset, x_offset = anchor.offset(len(message), max(len(line) for line in message))

        y = int(vertical * y_max + y_offset)
        x = int(horizontal * x_max + x_offset)
        return y, x

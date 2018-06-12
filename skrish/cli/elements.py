"""Contains and manages different elements available to be attached to screens.
"""
import curses
import time
from typing import Tuple

from skrish.cli.screen import Screen
from skrish.cli.util import Anchor


class Element:
    """Basic abstract element.
    """
    _screen: Screen
    vertical: float
    horizontal: float
    offset: Tuple[int, int]
    anchor: Anchor

    __should_display: bool

    def __init__(self, screen: Screen, vertical: float, horizontal: float, *,
                 offset: Tuple[int, int] = (0, 0), anchor: Anchor = Anchor.CENTER_CENTER) -> None:
        """Initialize this element with basic attributes.
        """
        self._screen = screen
        self.vertical = vertical
        self.horizontal = horizontal
        self.offset = offset
        self.anchor = anchor
        self.__should_display = True

    def set_position(self, vertical: float = None, horizontal: float = None,
                     offset: Tuple[int, int] = None, anchor: Anchor = None) -> None:
        """Set the position of this element in <vertical> and <horizontal> percentages of the screen with given
        <anchor> and <offset>. All parameters are optional and not inputting anything will not change the value.
        """
        if vertical is not None:
            self.vertical = vertical
        if horizontal is not None:
            self.horizontal = horizontal
        if offset is not None:
            self.offset = offset
        if anchor is not None:
            self.anchor = anchor

    def set_screen(self, screen: Screen, display: bool = True) -> Screen:
        """Set the <screen> that this element is attached to, and display it. If <display> is set to False,
        the element will not be flagged for display."""
        past_screen = self._screen
        self._screen = screen
        if display:
            self.update()
        return past_screen

    def should_display(self) -> bool:
        """Get whether or not this element is queued to be displayed.
        """
        return self.__should_display

    def update(self, display: bool = True) -> None:
        """Update this element and set it to be displayed, it can be held from display if <display> is set to False.
        """
        if display:
            self.__should_display = True

    def display(self) -> None:
        """Display this element on the set screen.
        """
        raise NotImplementedError

    def _move_pre(self) -> None:
        """Take pre-movement actions.
        """
        pass

    def _move_post(self) -> None:
        """Take post-movement actions.
        """
        pass

    def move(self, secs: float, *,
             vertical: float = 0, horizontal: float = 0, skippable: bool = True) -> None:
        """Move this element in <secs> seconds a delta of <vertical> and <horizontal> percentages of the screen.
        If <skippable> is set, then the animation can be skipped.
        """
        self._move_pre()

        if skippable:
            self._screen.stdscr.nodelay(True)

        start_vertical, start_horizontal = self.vertical, self.horizontal

        i = 0
        last_time = time.time()
        while i < 1:
            if skippable and self._screen.stdscr.getch() > 0:
                self._screen.clear()
                i = 1

            # Manage timing
            cur_time = time.time()
            deltatime, last_time = cur_time - last_time, cur_time
            i += deltatime / secs
            if i > 1:
                i = 1

            # Interpolate between the two points
            self.vertical = start_vertical + i * vertical
            self.horizontal = start_horizontal + i * horizontal

            self.display()

        if skippable:
            self._screen.stdscr.nodelay(False)

        self._move_post()


class ElementContainer:
    """Contains elements and allows easier batch management.
    """
    def __init__(self) -> None:
        """Initialize this element watcher.
        """
        self.elements = []

    def add_element(self, element: Element) -> None:
        """Add the given element to the screen.
        """
        self.elements.append(element)

    def update(self) -> None:
        """Update this screen and all elements within it.
        """
        for element in self.elements:
            element.update(True)

    def display(self) -> None:
        """Display all updated elements set to be displayed. Elements are automatically set to be displayed after
        being updated unless otherwise flagged.
        """
        for element in self.elements:
            if element.should_display():
                element.display(self)


class BasicTextElement(Element):
    """Basic text element.
    """
    text: str
    style: int

    def __init__(self, screen: Screen, vertical: float, horizontal: float, text: str, *,
                 offset: Tuple[int, int] = (0, 0), anchor: Anchor = Anchor.CENTER_CENTER,
                 style: int = curses.A_NORMAL) -> None:
        """Initialize this element with basic attributes and text attributes.
        """
        super(BasicTextElement, self).__init__(screen, vertical, horizontal, offset=offset, anchor=anchor)
        self.text = text
        self.style = style

    def update(self, display: bool = True) -> None:
        super(BasicTextElement, self).update(display)

    def display(self) -> None:
        text_list = self.text.strip("\n").split("\n")

        y_max, x_max = self._screen.stdscr.getmaxyx()
        y, x = self._screen.position_message(text_list, self.anchor, self.vertical, self.horizontal)

        num_lines = len(text_list)
        max_line = max(len(line) for line in text_list)
        counter = 0

        # FIXME: moving out of bottom-right corner crashes
        # If the message is out of bounds, then cut it off to prevent an error considering the manual offset
        new_text_list = text_list
        if y + self.offset[0] < 0:
            new_text_list = text_list[-(y + self.offset[0]):]
            y = self.offset[0]
        if y + self.offset[0] + num_lines > y_max:
            if y + self.offset[0] > y_max:
                y = y_max - self.offset[0]
            new_text_list = text_list[:y_max - (y + self.offset[0])]

        if x + self.offset[1] < 0:
            new_text_list = [line[-(x + self.offset[1]):] for line in new_text_list]
            x = self.offset[1]
        if x + self.offset[1] + max_line > x_max:
            if x + self.offset[1] > x_max:
                x = x_max - self.offset[1]
            new_text_list = [line[:x_max - (x + self.offset[1])] for line in new_text_list]

        for line in new_text_list:
            if not line:
                continue

            cursor_y, cursor_x = self._screen.stdscr.getyx()

            self._screen.stdscr.addstr((y if y is not None else cursor_y) + counter + self.offset[0],
                                       (x if x is not None else cursor_x) + self.offset[1],
                                       line, self.style)
            counter += 1

    def _move_pre(self) -> None:
        # Pad the message with spaces to not need to clear
        text_list = self.text.strip("\n").split("\n")

        h_padding, v_padding = " ", (" " * max(len(line) for line in text_list) if text_list else 0)
        text_list = [(h_padding + line + h_padding) for line in text_list]

        self.text = (v_padding + "\n") + ("\n".join(text_list)) + ("\n" + v_padding)

    def _move_post(self) -> None:
        # Removing the padding added before
        text_list = self.text.strip("\n").split("\n")

        text_list = [line[1:-1] for line in text_list[1:-1]]
        self.text = "\n".join(text_list)

# class Menu:
#     """Menu object that allows selection of a number of options.
#     """
#     screen: 'Screen'
#     options: List[Tuple[str, Callable[[], Any], bool]]
#     vertical: float
#     horizontal: float
#     anchor: Anchor = Anchor.CENTER_CENTER
#     offset: Tuple[int, int]
#     spacing: int
#     min_width: int
#     edges: Tuple[str, str]
#     selected_style = curses.A_STANDOUT
#
#     selection: int
#
#     def __init__(self, screen: 'Screen',
#                  options: List[Tuple[str, Callable[[], Any], bool]],
#                  vertical: float = 0.5, horizontal: float = 0.5,
#                  anchor: Anchor = Anchor.CENTER_CENTER, offset: Tuple[int, int] = (0, 0), spacing: int = 2,
#                  min_width: int = 10, edges: Tuple[str, str] = ("[", "]"),
#                  selected_style: int = curses.A_STANDOUT) -> None:
#         """Initialize a menu on the given <screen> with the given <options> which is a list of tuples that represents
#         the option name and action to take upon choosing it, and an optional flag to to state whether or not to stop
#         polling for this menu. The menu is positioned at <vertical> and <horizontal> percentages of the screen with
#         respect to an <anchor> and given <offset>. The vertical <spacing> between menu items can be specified as well
#         as the <min_width> of the items, which are terminated by the left and right <edges>, a 2-tuple.
#         A <selected_style> is applied the currently selected item.
#         """
#         self.screen = screen
#         self.options = options
#         self.vertical, self.horizontal = vertical, horizontal
#         self.anchor = anchor
#         self.offset = offset
#         self.spacing = spacing
#         self.min_width = min_width
#         self.edges = edges
#         self.selected_style = selected_style
#
#         self.selection = 0
#
#         self.update()
#
#     def up(self) -> None:
#         """Go up in the list.
#         """
#         self.selection -= 1
#         self.selection %= len(self.options)
#         self.update()
#
#     def down(self) -> None:
#         """Go down in the list.
#         """
#         self.selection += 1
#         self.selection %= len(self.options)
#         self.update()
#
#     def select(self) -> Optional[Callable[[], Any]]:
#         """Select the currently highlighted option.
#         """
#         call = self.options[self.selection][1]
#         if self.options[self.selection][2]:
#             return call
#
#         call()
#
#     def update(self) -> None:
#         """Update this menu's screen with its information.
#         """
#         width = max(self.min_width, max(len(option[0]) for option in self.options))
#         for i, option in enumerate(self.options):
#             message = option[0]
#             message = self.edges[0] + message.center(width) + self.edges[1]
#
#             self.screen.put(message, self.vertical, self.horizontal,
#                             ColorPair.SELECTED.pair |
#                             self.selected_style if self.selection == i else curses.A_NORMAL,
#                             anchor=self.anchor, offset=(i * self.spacing + self.offset[0], self.offset[1]))
#
#     def get_standard_keybinds(self) -> List[Tuple[str, List[int], str, Callable[[], Any], bool]]:
#         """Get the standard keybinds for menu navigation.
#         """
#         return [
#             ("up", [curses.KEY_UP], "select above", self.up, False),
#             ("down", [curses.KEY_DOWN], "select below", self.down, False),
#             ("enter", [curses.KEY_ENTER, 10], "select", self.select, False)
#         ]
#
#     def attach_spinners(self, spinners: List['Spinner'], gap: float = 0.05) -> None:
#         """Attach the given <spinners> to this menu with the given <gap>.
#         """
#         for i in range(min(len(spinners), len(self.options))):
#             spinners[i].set_position(self.vertical, self.horizontal + gap, Anchor.CENTER_LEFT,
#                                      offset=(i * self.spacing + self.offset[0], self.offset[1]))
#             spinners[i].screen = self.screen
#             spinners[i].update()
#
#
# class Spinner:
#     """Spinner object allowing selection of different values.
#     """
#     screen: 'Screen'
#     min_value: int
#     inital_value: int
#     max_value: int
#     step_value: int
#
#     vertical: float
#     horizontal: float
#     anchor: Anchor
#     offset: Tuple[int, int]
#
#     value: int
#
#     def __init__(self, screen: 'Screen',
#                  min_value: Optional[int] = None, initial_value: int = 0, max_value: Optional[int] = None,
#                  step_value: int = 1, vertical: float = 0, horizontal: float = 0,
#                  anchor: Anchor = Anchor.TOP_LEFT, offset: Tuple[int, int] = (0, 0)) -> None:
#         """Initialize a spinner with the given <min_value>, <initial_value>, <max_value> and <step_value> positioned
#         at <vertical> and <horizontal> percentages of the screen with the given <anchor> and the given <offset>.
#         """
#         self.screen = screen
#         self.min_value = min_value
#         self.inital_value = initial_value
#         self.max_value = max_value
#         self.step_value = step_value
#
#         self.vertical = vertical
#         self.horizontal = horizontal
#         self.anchor = anchor
#         self.offset = offset
#
#         self.value = self.inital_value
#         self.edges = ("", "")
#
#     def increment(self, step: int = None) -> None:
#         """Increment the spinner by the step value or <step> if specified.
#         """
#         if step is None:
#             step = self.step_value
#
#         self.value += step
#         self.value = min(self.value, self.max_value if self.max_value is not None else self.value)
#         self.update()
#
#     def decrement(self, step: int = None) -> None:
#         """Decrement the spinner by the step value or <step> if specified.
#         """
#         if step is None:
#             step = self.step_value
#
#         self.value -= step
#         self.value = max(self.value, self.min_value if self.min_value is not None else self.value)
#         self.update()
#
#     def update(self) -> None:
#         """Update the spinner to display the current value.
#         """
#         max_digits = max(len(str(self.max_value)), len(str(self.min_value)))
#         padding = ""
#         if self.min_value < 0:
#             padding = " "
#
#         self.screen.put(self.edges[0] + padding + str(self.value).zfill(max_digits) + self.edges[1],
#                         self.vertical, self.horizontal, anchor=self.anchor, offset=self.offset)
#
#     def _clear_space(self) -> None:
#         """Put whitespace in place of the spinner value.
#         """
#         max_digits = max(len(str(self.max_value)), len(str(self.min_value)))
#         whitespace = " " * (max_digits + len(self.edges[0]) + len(self.edges[1]) + int(self.min_value < 0))
#         self.screen.put(whitespace, self.vertical, self.horizontal, anchor=self.anchor, offset=self.offset)
#
#     def generate_selected_method(self, controls_screen: 'Screen', listener_screen: 'Screen') -> Callable[[], Any]:
#         """Generate the `selected method`.
#         """
#         def selected():
#             self.edges = ("< ", " >")
#             self.update()
#
#             # FIXME: drawing of controls
#             controls_screen.watch_keys([
#                 ("left", [curses.KEY_LEFT], "decrement", self.decrement, False),
#                 ("right", [curses.KEY_RIGHT], "increment", self.increment, False),
#                 ("enter", [curses.KEY_ENTER, 10], "main menu", lambda: None, True)
#             ],
#                 vertical=0, horizontal=0, joiner="\n", anchor=Anchor.TOP_LEFT, offset=(1, 1),
#                 listener_screen=listener_screen
#             )
#
#             self._clear_space()
#             self.edges = ("", "")
#             self.update()
#
#         return selected
#
#     def set_position(self, vertical: Optional[float] = None, horizontal: Optional[float] = None,
#                      anchor: Optional[Anchor] = None, offset: Tuple[int, int] = None) -> None:
#         """Set all positional attributes of the spinner, any attribute not specified remains unchanged.
#         """
#         if vertical is not None:
#             self.vertical = vertical
#         if horizontal is not None:
#             self.horizontal = horizontal
#         if anchor is not None:
#             self.anchor = anchor
#         if offset is not None:
#             self.offset = offset

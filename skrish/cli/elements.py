"""Contains and manages different elements available to be attached to screens.
"""
import curses
import time
from collections import Iterable
from typing import Tuple, List, Callable, Any, Optional, Iterator, TypeVar, Generic, Dict, Union
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

        Basic elements are the <screen> in which this element should be and the <vertical> and <horizontal> percentages
        of the screen at which this element's <anchor> resides with <offset>.
        """
        self._screen = screen
        self.vertical = vertical
        self.horizontal = horizontal
        self.offset = offset
        self.anchor = anchor
        self.__should_display = True

        self.update()

    def set_position(self, *, vertical: float = None, horizontal: float = None,
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

    def update(self, *, display: bool = True) -> None:
        """Update this element and set it to be displayed, it can be held from display if <display> is set to False.
        """
        if display:
            self.__should_display = True

    def display(self) -> None:
        """Display this element on the set screen and refresh.
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
            # .getch() refreshes the screen, so only refresh if needed
            if not skippable:
                self._screen.stdscr.refresh()

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


T = TypeVar('T')


class ElementContainer(Iterable, Generic[T]):
    """Contains elements and allows easier batch management.
    """
    _elements: Dict[str, T]

    def __init__(self) -> None:
        """Initialize this element watcher.
        """
        self._elements = {}

    def __setitem__(self, identifier: str, element: T) -> None:
        self.add_element(identifier, element)

    def __getitem__(self, identifier: str) -> T:
        return self.get_element(identifier)

    def __iter__(self) -> Iterator:
        return iter(self._elements.values())

    def add_element(self, identifier: str, element: T) -> None:
        """Add the <element> to the container with <identifier>.
        """
        self._elements[identifier] = element

    def get_element(self, identifier: str) -> T:
        """Get the element with the given <identifier> in the container.
        """
        return self._elements[identifier]

    def update(self) -> None:
        """Update this screen and all elements within it.
        """
        for element in self._elements.values():
            element.update()

    def display(self) -> None:
        """Display all updated elements set to be displayed. Elements are automatically set to be displayed after
        being updated unless otherwise flagged.
        """
        for element in self._elements.values():
            if element.should_display():
                element.display()


class BasicTextElement(Element):
    """Basic text element.
    """
    text: str
    style: int

    def __init__(self, screen: Screen, vertical: float, horizontal: float, text: str, *,
                 offset: Tuple[int, int] = (0, 0), anchor: Anchor = Anchor.CENTER_CENTER,
                 style: int = curses.A_NORMAL) -> None:
        """Initialize this basic text element with basic attributes and text attributes.

        Text attributes are the <text> to be displayed in a <style>.
        """
        super(BasicTextElement, self).__init__(screen, vertical, horizontal, offset=offset, anchor=anchor)
        self.text = text
        self.style = style

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

        self._screen.stdscr.refresh()

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


# TODO: replace with MenuItemElement
class MenuTextElement(BasicTextElement):
    """Menu text element for easier text element use with menus. Must be used inside a menu.
    """

    def __init__(self, text: str, style: int = curses.A_NORMAL) -> None:
        # noinspection PyTypeChecker
        super().__init__(None, 0, 0, text, style=style)


class MenuElement(Element):
    """Menu element that allows selection of a number of options.
    """
    options: List[Tuple[BasicTextElement, Callable[[], Any], bool]]
    spacing: int
    min_width: int
    edges: Tuple[str, str]
    selected_style: int

    selection: int
    __elements: ElementContainer[BasicTextElement]

    def __init__(self, screen: Screen, vertical: float, horizontal: float,
                 options: List[Tuple[Union[BasicTextElement, str], Callable[[], Any], bool]], *,
                 offset: Tuple[int, int] = (0, 0), anchor: Anchor = Anchor.CENTER_CENTER,
                 spacing: int = 2, min_width: int = 0, edges: Tuple[str, str] = ("[", "]"),
                 initial_selection: int = -1, selected_style: int = curses.A_STANDOUT) -> None:
        """Initialize this menu element with basic attributes and menu attributes.

        Menu attributes are the <options> to include which consists of a list of tuples each representing an entry
        consisting of a BasicTextElement, callable action function, and whether or not this action should end the menu.
        In addition, <spacing> between elements, <min_width> of each element, <edges> to delimit each entry,
        and the style of the current selection <selected_style> can all be set.
        """
        super().__init__(screen, vertical, horizontal, offset=offset, anchor=anchor)
        self.options = options
        self.spacing = spacing
        self.min_width = min_width
        self.edges = edges
        self.selected_style = selected_style

        self.selection = initial_selection
        self.__elements = ElementContainer()
        for i, option in enumerate(options):
            element = option[0] if isinstance(option[0], MenuTextElement) else MenuTextElement(option[0])
            self.__elements.add_element(str(i), element)

    def display(self) -> None:
        width = max(self.min_width, max(len(element.text) for element in self.__elements))
        for i, element in enumerate(self.__elements):
            if not (element.text[0] == self.edges[0] and element.text[-1] == self.edges[1]):
                element.text = self.edges[0] + element.text.center(width) + self.edges[1]
            element.style = self.selected_style if self.selection == i else curses.A_NORMAL
            element.set_position(vertical=self.vertical,
                                 horizontal=self.horizontal,
                                 offset=(self.offset[0] + i * self.spacing, self.offset[1]),
                                 anchor=self.anchor)
            element.set_screen(self._screen)
            element.update()
        self.__elements.display()
        self._screen.stdscr.refresh()

    def up(self) -> None:
        """Go up in the list.
        """
        self.selection -= 1
        self.selection %= len(self.options)
        self.display()

    def down(self) -> None:
        """Go down in the list.
        """
        self.selection += 1
        self.selection %= len(self.options)
        self.display()

    def select(self) -> Optional[Callable[[], Any]]:
        """Select the currently highlighted option.
        """
        if self.selection < 0:
            return

        call = self.options[self.selection][1]
        if self.options[self.selection][2]:
            return call
        call()

    def get_standard_keybinds(self) -> List[Tuple[str, List[int], str, Callable[[], Any], bool]]:
        """Get the standard keybinds for menu navigation.
        """
        return [
            ("up", [curses.KEY_UP], "select above", self.up, False),
            ("down", [curses.KEY_DOWN], "select below", self.down, False),
            ("enter", [curses.KEY_ENTER, 10], "select", self.select, False)
        ]
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

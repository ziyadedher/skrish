"""Provides useful CLI utilities for more efficient displaying of information.
"""
from typing import Any, Tuple, List, Callable, Optional
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


class Menu:
    """Menu object that allows selection of a number of options.
    """
    screen: 'Screen'
    options: List[Tuple[str, Callable[[], Any], bool]]
    vertical: float
    horizontal: float
    anchor: Anchor = Anchor.CENTER_CENTER
    offset: Tuple[int, int]
    spacing: int
    min_width: int
    edges: Tuple[str, str]
    selected_style = curses.A_STANDOUT

    selection: int

    def __init__(self, screen: 'Screen',
                 options: List[Tuple[str, Callable[[], Any], bool]],
                 vertical: float = 0.5, horizontal: float = 0.5,
                 anchor: Anchor = Anchor.CENTER_CENTER, offset: Tuple[int, int] = (0, 0), spacing: int = 2,
                 min_width: int = 10, edges: Tuple[str, str] = ("[", "]"),
                 selected_style: int = curses.A_STANDOUT) -> None:
        """Initialize a menu on the given <screen> with the given <options> which is a list of tuples that represents
        the option name and action to take upon choosing it, and an optional flag to to state whether or not to stop
        polling for this menu. The menu is positioned at <vertical> and <horizontal> percentages of the screen with
        respect to an <anchor> and given <offset>. The vertical <spacing> between menu items can be specified as well
        as the <min_width> of the items, which are terminated by the left and right <edges>, a 2-tuple.
        A <selected_style> is applied the currently selected item.
        """
        self.screen = screen
        self.options = options
        self.vertical, self.horizontal = vertical, horizontal
        self.anchor = anchor
        self.offset = offset
        self.spacing = spacing
        self.min_width = min_width
        self.edges = edges
        self.selected_style = selected_style

        self.selection = 0

        self.update()

    def up(self) -> None:
        """Go up in the list.
        """
        self.selection -= 1
        self.selection %= len(self.options)
        self.update()

    def down(self) -> None:
        """Go down in the list.
        """
        self.selection += 1
        self.selection %= len(self.options)
        self.update()

    def select(self) -> Optional[Callable[[], Any]]:
        """Select the currently highlighted option.
        """
        call = self.options[self.selection][1]
        if self.options[self.selection][2]:
            return call

        call()

    def update(self) -> None:
        """Update this menu's screen with its information.
        """
        width = max(self.min_width, max(len(option[0]) for option in self.options))
        for i, option in enumerate(self.options):
            message = option[0]
            message = self.edges[0] + message.center(width) + self.edges[1]

            self.screen.put(message, self.vertical, self.horizontal,
                            ColorPair.SELECTED.pair |
                            self.selected_style if self.selection == i else curses.A_NORMAL,
                            anchor=self.anchor, offset=(i * self.spacing + self.offset[0], self.offset[1]))

    def get_standard_keybinds(self) -> List[Tuple[str, List[int], str, Callable[[], Any], bool]]:
        """Get the standard keybinds for menu navigation.
        """
        return [
            ("up", [curses.KEY_UP], "select above", self.up, False),
            ("down", [curses.KEY_DOWN], "select below", self.down, False),
            ("enter", [curses.KEY_ENTER, 10], "select", self.select, False)
        ]

    def attach_spinners(self, spinners: List['Spinner'], gap: float = 0.05) -> None:
        """Attach the given <spinners> to this menu with the given <gap>.
        """
        for i in range(min(len(spinners), len(self.options))):
            spinners[i].set_position(self.vertical, self.horizontal + gap, Anchor.CENTER_LEFT,
                                     offset=(i * self.spacing + self.offset[0], self.offset[1]))
            spinners[i].screen = self.screen
            spinners[i].update()


class Spinner:
    """Spinner object allowing selection of different values.
    """
    screen: 'Screen'
    min_value: int
    inital_value: int
    max_value: int
    step_value: int

    vertical: float
    horizontal: float
    anchor: Anchor
    offset: Tuple[int, int]

    value: int

    def __init__(self, screen: 'Screen',
                 min_value: Optional[int] = None, initial_value: int = 0, max_value: Optional[int] = None,
                 step_value: int = 1, vertical: float = 0, horizontal: float = 0,
                 anchor: Anchor = Anchor.TOP_LEFT, offset: Tuple[int, int] = (0, 0)) -> None:
        """Initialize a spinner with the given <min_value>, <initial_value>, <max_value> and <step_value> positioned
        at <vertical> and <horizontal> percentages of the screen with the given <anchor> and the given <offset>.
        """
        self.screen = screen
        self.min_value = min_value
        self.inital_value = initial_value
        self.max_value = max_value
        self.step_value = step_value

        self.vertical = vertical
        self.horizontal = horizontal
        self.anchor = anchor
        self.offset = offset

        self.value = self.inital_value
        self.edges = ("", "")

    def increment(self, step: int = None) -> None:
        """Increment the spinner by the step value or <step> if specified.
        """
        if step is None:
            step = self.step_value

        self.value += step
        self.value = min(self.value, self.max_value if self.max_value is not None else self.value)
        self.update()

    def decrement(self, step: int = None) -> None:
        """Decrement the spinner by the step value or <step> if specified.
        """
        if step is None:
            step = self.step_value

        self.value -= step
        self.value = max(self.value, self.min_value if self.min_value is not None else self.value)
        self.update()

    def update(self) -> None:
        """Update the spinner to display the current value.
        """
        max_digits = max(len(str(self.max_value)), len(str(self.min_value)))
        padding = ""
        if self.min_value < 0:
            padding = " "

        self.screen.put(self.edges[0] + padding + str(self.value).zfill(max_digits) + self.edges[1],
                        self.vertical, self.horizontal, anchor=self.anchor, offset=self.offset)

    def _clear_space(self) -> None:
        """Put whitespace in place of the spinner value.
        """
        max_digits = max(len(str(self.max_value)), len(str(self.min_value)))
        whitespace = " " * (max_digits + len(self.edges[0]) + len(self.edges[1]) + int(self.min_value < 0))
        self.screen.put(whitespace, self.vertical, self.horizontal, anchor=self.anchor, offset=self.offset)

    def generate_selected_method(self, controls_screen: 'Screen', listener_screen: 'Screen') -> Callable[[], Any]:
        """Generate the `selected method`.
        """
        def selected():
            self.edges = ("< ", " >")
            self.update()

            # FIXME: drawing of controls
            controls_screen.watch_keys([
                ("left", [curses.KEY_LEFT], "decrement", self.decrement, False),
                ("right", [curses.KEY_RIGHT], "increment", self.increment, False),
                ("enter", [curses.KEY_ENTER, 10], "main menu", lambda: None, True)
            ],
                vertical=0, horizontal=0, joiner="\n", anchor=Anchor.TOP_LEFT, offset=(1, 1),
                listener_screen=listener_screen
            )

            self._clear_space()
            self.edges = ("", "")
            self.update()

        return selected

    def set_position(self, vertical: Optional[float] = None, horizontal: Optional[float] = None,
                     anchor: Optional[Anchor] = None, offset: Tuple[int, int] = None) -> None:
        """Set all positional attributes of the spinner, any attribute not specified remains unchanged.
        """
        if vertical is not None:
            self.vertical = vertical
        if horizontal is not None:
            self.horizontal = horizontal
        if anchor is not None:
            self.anchor = anchor
        if offset is not None:
            self.offset = offset

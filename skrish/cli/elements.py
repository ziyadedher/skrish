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
            self.display()
        return past_screen

    def display(self) -> None:
        """Update and display this element on the set screen and refresh.
        """
        raise NotImplementedError

    def move(self, secs: float, *,
             vertical: float = 0, horizontal: float = 0, skippable: bool = True) -> None:
        """Move this element in <secs> seconds a delta of <vertical> and <horizontal> percentages of the screen.
        If <skippable> is set, then the animation can be skipped.
        """
        # Watch for keys without delay
        if skippable:
            self._screen.stdscr.nodelay(True)

        start_vertical, start_horizontal = self.vertical, self.horizontal

        i = 0
        last_time = time.time()
        while i < 1:
            # Check if any character was pressed to skip movement
            if skippable and self._screen.stdscr.getch() > 0:
                self._screen.clear()
                i = 1
            # .getch() refreshes the screen, so refresh only if required
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

        # Stop watching for keys without delay
        if skippable:
            self._screen.stdscr.nodelay(False)


T = TypeVar('T')


class ElementContainer(Iterable, Generic[T]):
    """Contains elements and allows easier batch management.
    """
    _elements: Dict[str, T]

    def __init__(self) -> None:
        """Initialize this element watcher.
        """
        # TODO: implement type checking that <T> is an actual element type, otherwise `self.display` will error
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

    def display(self) -> None:
        """Display all updated elements set to be displayed. Elements are automatically set to be displayed after
        being updated unless otherwise flagged.
        """
        for element in self._elements.values():
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
        super().__init__(screen, vertical, horizontal, offset=offset, anchor=anchor)
        self.text = text
        self.style = style

    def display(self) -> None:
        # Split the text up and strip any unneeded whitespace
        text_list = self.text.strip("\n").split("\n")

        y_max, x_max = self._screen.stdscr.getmaxyx()
        y, x = self._screen.position_message(text_list, self.anchor, self.vertical, self.horizontal)

        # FIXME: moving out of bottom-right corner crashes
        # Cut off vertical out-of-bounds lines of the text
        num_lines = len(text_list)
        if y + self.offset[0] < 0:
            text_list = text_list[-(y + self.offset[0]):]
            y = self.offset[0]
        if y + self.offset[0] + num_lines > y_max:
            if y + self.offset[0] > y_max:
                y = y_max - self.offset[0]
            text_list = text_list[:y_max - (y + self.offset[0])]

        # Cut off line out-of-bounds beginnings or ends
        max_line = max(len(line) for line in text_list)
        if x + self.offset[1] < 0:
            text_list = [line[-(x + self.offset[1]):] for line in text_list]
            x = self.offset[1]
        if x + self.offset[1] + max_line > x_max:
            if x + self.offset[1] > x_max:
                x = x_max - self.offset[1]
            text_list = [line[:x_max - (x + self.offset[1])] for line in text_list]

        # Display every line that needs to be displayed in its correct location
        counter = 0
        for line in text_list:
            if not line:
                continue

            cursor_y, cursor_x = self._screen.stdscr.getyx()
            self._screen.stdscr.addstr((y if y is not None else cursor_y) + counter + self.offset[0],
                                       (x if x is not None else cursor_x) + self.offset[1],
                                       line, self.style)
            counter += 1

        self._screen.stdscr.refresh()

    def move(self, *args, **kwargs) -> None:
        # Pad the message with spaces to not need to clear after every step of movement
        text_list = self.text.strip("\n").split("\n")
        h_padding, v_padding = " ", (" " * max(len(line) for line in text_list) if text_list else 0)
        text_list = [(h_padding + line + h_padding) for line in text_list]
        self.text = (v_padding + "\n") + ("\n".join(text_list)) + ("\n" + v_padding)

        super().move(*args, **kwargs)

        # Removing the padding added before
        text_list = self.text.strip("\n").split("\n")
        text_list = [line[1:-1] for line in text_list[1:-1]]
        self.text = "\n".join(text_list)

    def _clear(self, length: int, height: int = 1) -> None:
        """Clear this element with whitespace of length <length> and height <height>.
        """
        # Set the text to whitespace
        past_text = self.text
        self.text = "\n".join((" " * length) * height)

        # Make sure we use the regular display function rather than whatever the subclasses function is
        if type(self) is not BasicTextElement:
            super(type(self), self).display()
        else:
            self.display()

        # Revert the text
        self.text = past_text


class SpinnerElement(BasicTextElement):
    """Spinner element representing an interactive value chooser.
    """
    step_value: int
    edges: Tuple[str, str]
    selected_style: int
    selected_edges: Tuple[str, str]
    min_value: Optional[int]
    value: int
    max_value: Optional[int]
    label_gap: float
    label_element: Optional[BasicTextElement]

    def __init__(self, screen: Screen, vertical: float, horizontal: float, step_value: int, *,
                 offset: Tuple[int, int] = (0, 0), anchor: Anchor = Anchor.CENTER_CENTER,
                 style: int = curses.A_NORMAL, edges: Tuple[str, str] = ("[", "]"), selected_style: int = curses.A_BOLD,
                 selected_edges: Tuple[str, str] = ("<", ">"), min_value: Optional[int] = None,
                 initial_value: int = 0, max_value: Optional[int] = None,
                 label: str = "", label_gap: float = 0.1) -> None:
        """Initialize this spinner element with basic attributes, text attributes, and spinner attributes.

        No <text> attribute is required for the spinner.

        Spinner attributes are <step_value> representing the step to take through each increment or decrement, the
        <edges> around the spinner and the <selected_style> and <selected_edges> to set to be the style and edges when
        selected, the <min_value>, <initial_value>, and <max_value>, and a <label> with <label_gap> representing a piece
        of text placed before the spinner in percentage gap.
        """
        super().__init__(screen, vertical, horizontal, str(initial_value), offset=offset, anchor=anchor, style=style)

        self.step_value = step_value
        self.edges = edges
        self.selected_style = selected_style
        self.selected_edges = selected_edges
        self.min_value = min_value
        self.value = initial_value
        self.max_value = max_value
        self.label_gap = label_gap

        # Only create a valid label element if the label has been set
        if label:
            self.label_element = BasicTextElement(screen, self.horizontal, self.vertical, label,
                                                  anchor=Anchor.CENTER_LEFT, offset=self.offset)
        else:
            self.label_element = None

    def increment(self, step: int = None) -> None:
        """Increment the spinner by the step value or <step> if specified.
        """
        if step is None:
            step = self.step_value

        # Update the value, text, and display
        self.value += step
        self.value = min(self.value, self.max_value if self.max_value is not None else self.value)
        self.text = str(self.value)
        self.display()

    def decrement(self, step: int = None) -> None:
        """Decrement the spinner by the step value or <step> if specified.
        """
        if step is None:
            step = self.step_value

        # Update the value, text, and display
        self.value -= step
        self.value = max(self.value, self.min_value if self.min_value is not None else self.value)
        self.text = str(self.value)
        self.display()

    def display(self) -> None:
        max_digits = max(len(str(self.max_value)), len(str(self.min_value)))
        max_edges = max(len(str(self.edges[0] + self.edges[1])),
                        len(str(self.selected_edges[0] + self.selected_edges[1])))

        # Apply the edges before displaying
        self.text = self.edges[0] + self.text.center(max_digits) + self.edges[1]

        # Display the label if required, pushing the spinner to the side
        if self.label_element:
            self.horizontal += self.label_gap
            self._clear(max_digits + max_edges)
            super().display()
            self.horizontal -= self.label_gap

            self.label_element.set_position(vertical=self.vertical, horizontal=self.horizontal, offset=self.offset)
            self.label_element.display()
        else:
            self._clear(max_digits + max_edges)
            super().display()

        # Remove the edges from the text
        self.text = self.text[1:-1]

    def generate_selected_method(self, listener_screen: 'Screen') -> Callable[[], Any]:
        """Generate the `selected method`.
        """
        # TODO: reimplement, this sucks
        def selected():
            previous_edges = self.edges
            self.edges = self.selected_edges
            self.display()

            listener_screen.watch_keys([
                ("left", [curses.KEY_LEFT], "decrement", self.decrement, False),
                ("right", [curses.KEY_RIGHT], "increment", self.increment, False),
                ("enter", [curses.KEY_ENTER, 10], "back", lambda: None, True)
            ],
                vertical=0, horizontal=0, joiner="\n", anchor=Anchor.TOP_LEFT, offset=(1, 1),
                listener_screen=listener_screen
            )

            self.edges = previous_edges
            self.display()

        return selected


class MenuListElement(Element):
    """Menu list element that allows selection of a number of options.
    """
    options: List[Tuple[Union[Element, str], Callable[[], Any], bool]]
    spacing: int
    min_width: int
    edges: Tuple[str, str]
    selected_style: int

    selection: int
    __elements: ElementContainer[Element]

    def __init__(self, screen: Screen, vertical: float, horizontal: float,
                 options: List[Tuple[Union[Element, str], Callable[[], Any], bool]], *,
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

        # Grab all of the menu items and store them, generating basic text elements if required
        self.__elements = ElementContainer()
        for i, option in enumerate(options):
            element = option[0] if isinstance(option[0], Element) else BasicTextElement(screen, 0, 0, option[0])
            self.__elements.add_element(str(i), element)

        self.options = options
        self.spacing = spacing
        self.min_width = min_width
        self.edges = edges
        self.selected_style = selected_style

        self.selection = initial_selection

    def display(self) -> None:
        width = max(self.min_width, max(len(element.text) for element in self.__elements))
        for i, element in enumerate(self.__elements):
            # If the element is text and does not have the required edges, apply them
            if isinstance(element, BasicTextElement) and len(element.text) > 0:
                if not (element.text[0] == self.edges[0] and element.text[-1] == self.edges[1]):
                    element.text = self.edges[0] + element.text.center(width) + self.edges[1]

            # Display the element in the correct positioning
            element.style = self.selected_style if self.selection == i else curses.A_NORMAL
            element.set_position(vertical=self.vertical,
                                 horizontal=self.horizontal,
                                 offset=(self.offset[0] + i * self.spacing, self.offset[1]),
                                 anchor=self.anchor)
            element.set_screen(self._screen)
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
        # TODO: probably want to rework the whole selection system
        if self.selection < 0:
            return

        call = self.options[self.selection][1]
        if self.options[self.selection][2]:
            return call
        call()

    def get_standard_keybinds(self) -> List[Tuple[str, List[int], str, Callable[[], Any], bool]]:
        """Get the standard keybinds for menu navigation.
        """
        # TODO: reimplement, this sucks
        return [
            ("up", [curses.KEY_UP], "select above", self.up, False),
            ("down", [curses.KEY_DOWN], "select below", self.down, False),
            ("enter", [curses.KEY_ENTER, 10], "select", self.select, False)
        ]

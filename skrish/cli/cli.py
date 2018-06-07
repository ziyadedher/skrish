"""Contains main command-line interface code for interacting with the game.
"""
import curses

from skrish.cli import util


class Interface:
    """Manages the command-line interface on a high-level.
    """

    def __init__(self) -> None:
        """Initialize the command-line interface.
        """
        self.__screen = curses.initscr()

    def __enter__(self) -> 'Interface':
        """Called upon calling the interface using `with`.
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Called upon exiting the scope of the interface using `with`.
        """
        self.exit()

    def start(self) -> None:
        """Start the interface.
        """
        self.__curses_config()

    def error(self, message: str) -> None:
        """Display an error <message> to screen and wait for user input.
        """
        top_bar_message = "Oops! Something went wrong and an error has occured."

        self.__screen.clear()
        self.__screen.border()

        y, x = util.positionyx(self.__screen, top_bar_message, vertical=0.1, horizontal=0.5)
        self.__screen.addstr(y, x, top_bar_message, util.ColorPair.ERROR.pair)

        self.__screen.addstr(*util.centeryx(self.__screen, message), message)

        self.__screen.refresh()
        self.__screen.getkey()

    def exit(self) -> None:
        """Exit the interface cleanly with no error.
        """
        self.__curses_deconfig()
        curses.endwin()

    def __curses_config(self) -> None:
        """Configure curses to default game settings.
        """
        curses.noecho()                    # Do not display typed keys by default
        curses.cbreak()                    # Do not wait for `ENTER` key to read keystrokes
        curses.curs_set(0)                 # Do not display the cursor
        curses.start_color()               # Allow coloring
        util.ColorPair.init_color_pairs()  # Initialize custom color pairs
        self.__screen.keypad(True)         # Parse weird keys

    def __curses_deconfig(self) -> None:
        """Deconfigure curses to revert nice terminal settings.
        """
        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        self.__screen.keypad(False)

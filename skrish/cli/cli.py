"""Contains main command-line interface code for interacting with the game.
"""
import curses

from skrish.cli import util
from skrish.cli.screen import Screen
from skrish.game.game import Game


class Interface:
    """Manages and controls the flow of game scenes.
    """
    class __Interface:
        screen: Screen
        game: Game

        def __init__(self, game: Game) -> None:
            """Initialize the command-line interface.
            """
            self.screen = None
            self.scene_manager = None
            self.game = game

        def start(self) -> None:
            """Start the interface.
            """
            self.screen = Screen(curses.initscr())
            self.__curses_config()

        @staticmethod
        def call_scene(identifier: str) -> None:
            """Call the scene with the given <identifier>.
            """
            from skrish.cli.scene_manager import call_scene
            call_scene(identifier)

        def error(self, message: str) -> None:
            """Display an error <message> to screen and wait for user input.
            """
            top_bar_message = "Oops! Something went wrong and an error has occured."

            self.screen.clear()
            self.screen.border()

            self.screen.display(top_bar_message,
                                *self.screen.positionyx(top_bar_message, vertical=0.1, horizontal=0.5),
                                util.ColorPair.ERROR.pair)

            self.screen.display(message,
                                *self.screen.positionyx(message, vertical=0.5, horizontal=0.5),
                                util.ColorPair.STANDARD.pair)

            self.screen.refresh()
            self.screen.getkey()

        def exit(self) -> None:
            """Exit the interface cleanly with no error.
            """
            self.__curses_deconfig()
            curses.endwin()

        def __curses_config(self) -> None:
            """Configure curses to default game settings.
            """
            curses.noecho()  # Do not display typed keys by default
            curses.cbreak()  # Do not wait for `ENTER` key to read keystrokes
            curses.curs_set(0)  # Do not display the cursor
            curses.start_color()  # Allow coloring
            util.ColorPair.init_color_pairs()  # Initialize custom color pairs
            self.screen.keypad(True)  # Parse weird keys

        def __curses_deconfig(self) -> None:
            """Deconfigure curses to revert nice terminal settings.
            """
            curses.echo()
            curses.nocbreak()
            curses.curs_set(1)
            self.screen.keypad(False)

    instance: __Interface = None

    def __init__(self, game: Game):
        if not Interface.instance:
            Interface.instance = Interface.__Interface(game)
        else:
            Interface.instance.game = game

    def __getattr__(self, name: str):
        return getattr(self.instance, name)

    def __enter__(self):
        """Called upon calling the interface using `with`.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Called upon exiting the scope of the interface using `with`.
        """
        self.exit()
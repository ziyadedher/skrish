"""Contains pre-made scenes for the interface.
"""
import curses
from typing import Tuple, List, Callable, Any

from skrish.cli import util
from skrish.cli.scene_manager import Scene, SceneManager
from skrish.cli.cli import Interface
from skrish.cli.screen import Screen

from skrish.game.game import Game


TITLE = """
    ▄████████    ▄█   ▄█▄    ▄████████  ▄█     ▄████████    ▄█    █▄    
  ███    ███   ███ ▄███▀   ███    ███ ███    ███    ███   ███    ███   
  ███    █▀    ███▐██▀     ███    ███ ███▌   ███    █▀    ███    ███   
  ███         ▄█████▀     ▄███▄▄▄▄██▀ ███▌   ███         ▄███▄▄▄▄███▄▄ 
▀███████████ ▀▀█████▄    ▀▀███▀▀▀▀▀   ███▌ ▀███████████ ▀▀███▀▀▀▀███▀  
         ███   ███▐██▄   ▀███████████ ███           ███   ███    ███   
   ▄█    ███   ███ ▀███▄   ███    ███ ███     ▄█    ███   ███    ███   
 ▄████████▀    ███   ▀█▀   ███    ███ █▀    ▄████████▀    ███    █▀    
               ▀           ███    ███                                  
"""

interface = Interface.instance
screen: Screen = interface.screen
game: Game = interface.game

register_scene = SceneManager.register_scene
call_scene = SceneManager.call_scene
can_go_back = SceneManager.can_go_back
go_back = SceneManager.go_back


@register_scene("intro")
class IntroScene(Scene):
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx(TITLE, vertical=0.5, horizontal=0.5)
        start = -max(len(line) for line in TITLE.split("\n"))
        screen.scroll_message(TITLE, 2, center_y - 10, start, center_y - 10, center_x,
                              util.ColorPair.TITLE.pair, skippable=True)


@register_scene("main_menu")
class MainMenuScene(Scene):
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx(TITLE, vertical=0.5, horizontal=0.5)
        screen.display(TITLE, center_y - 10, center_x, util.ColorPair.TITLE.pair)

        menu = _generate_menu([
            ("START", lambda: call_scene("character_creation")),
            ("OPTIONS", lambda: call_scene("options")),
            ("CREDITS", lambda: call_scene("credits")),
            ("QUIT", lambda: call_scene("quit"))
        ], min_width=25, selected_style=curses.A_BOLD)

        _watch_keys(menu)


@register_scene("options")
class OptionsScene(Scene):
    def display(self) -> None:
        screen.clear()

        _title("OPTIONS")

        _watch_keys()


@register_scene("credits")
class CreditsScene(Scene):
    def display(self) -> None:
        screen.clear()

        _title("CREDITS")

        text = "Ziyad Edher"
        screen.display(text, *screen.positionyx(text, vertical=0.5, horizontal=0.5),
                       util.ColorPair.STANDARD.pair)

        _watch_keys()


@register_scene("quit")
class QuitScene(Scene):
    def display(self) -> None:
        screen.clear()

        _title("QUIT")

        text = "Are you sure you want to quit?"
        screen.display(text, *screen.positionyx(text, vertical=0.4, horizontal=0.5),
                       util.ColorPair.WARNING.pair)

        assert can_go_back()
        menu = _generate_menu([
            ("NO", go_back),
            ("YES", SceneManager.quit),
        ], min_width=10, selected_style=curses.A_BOLD)

        _watch_keys(menu)


@register_scene("character_creation")
class CharacterCreationScene(Scene):
    def display(self) -> None:
        screen.clear()

        y_max, x_max = screen.getmaxyx()
        main_params = (round(y_max * 0.75), round(x_max * 0.75), 0, 0)
        log_params = (y_max, round(x_max * 0.25), 0, round(x_max * 0.75))
        info_params = (round(y_max * 0.25), round(x_max * 0.75), round(y_max * 0.75), 0)

        log = Screen(screen.derwin(*log_params))
        info = Screen(screen.derwin(*info_params))
        main = Screen(screen.derwin(*main_params))

        main.box()
        log.box()
        info.box()

        _watch_keys()


def _generate_menu(options: List[Tuple[str, Callable[[], Any]]], spacing: int = 2, min_width: int = 0,
                   selected_style=curses.A_STANDOUT) -> List[Tuple[str, List[int], str, Callable[[], Any]]]:
    """Generate a menu with the given options.
    """
    screen.nodelay(True)

    num_selections = len(options)
    width = max(min_width, max(len(option[0]) for option in options))

    class Menu:
        actions: List[Callable[[], None]]
        selection: int

        def __init__(self, actions: List[Callable[[], None]]) -> None:
            self.actions = actions
            self.selection = 0

        def up(self) -> None:
            self.selection -= 1
            self.selection %= num_selections
            self.update()

        def down(self) -> None:
            self.selection += 1
            self.selection %= num_selections
            self.update()

        def select(self) -> None:
            self.actions[self.selection]()

        def update(self) -> None:
            for i, option in enumerate(options):
                message = option[0]
                message = "[ " + message.center(width) + " ]"
                center_y, center_x = screen.positionyx(message, vertical=0.5, horizontal=0.5)
                screen.display(message, center_y + i * spacing, center_x,
                               util.ColorPair.SELECTED.pair |
                               selected_style if self.selection == i else curses.A_NORMAL)

    menu = Menu([option[1] for option in options])
    menu.update()
    return [
        ("up", [curses.KEY_UP], "select above", menu.up),
        ("down", [curses.KEY_DOWN], "select below", menu.down),
        ("enter", [curses.KEY_ENTER, 10], "select", menu.select)
    ]


def _watch_keys(options: List[Tuple[str, List[int], str, Callable[[], Any]]] = None, joiner: str = "    ",
                show_keys: bool = True, callback: Callable[[int], Any] = lambda i: None) -> None:
    """Watch the keys given by <options> which describes a list of tuples of the form
    ("key name", keycode, "action name", action). These keys will be displayed at the bottom of the screen if
    <show_keys> is True, and a <callback> will be called while polling the keys.
    """
    if options is None:
        options = []

    if can_go_back():
        options.append(("backspace", [curses.KEY_BACKSPACE, 127], "back", go_back))

    if show_keys:
        text_array = []
        for option in options:
            text_array.append("[{}] {}".format(option[0], option[2]))

        text = joiner.join(text_array)
        screen.display(text, *screen.positionyx(text, vertical=0.95, horizontal=0.5))

    screen.nodelay(True)
    while True:
        key = screen.getch()
        callback(key)

        for option in options:
            if key in option[1]:
                screen.nodelay(False)
                option[3]()


def _title(text: str) -> None:
    """Display a title in the screen with the given <text>.
    """
    text = "==== {} ====".format(text)
    screen.display(text, *screen.positionyx(text, vertical=0.3, horizontal=0.5),
                   util.ColorPair.SUCCESS.pair)

"""Contains pre-made scenes for the interface.
"""
import curses
from typing import Tuple, List, Callable, Any

from skrish.cli import util
from skrish.cli.scene_manager import Scene, SceneManager
from skrish.cli.cli import Interface


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
screen = interface.screen
game = interface.game

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
            ("START", lambda: None),
            ("OPTIONS", lambda: call_scene("options")),
            ("CONTROLS", lambda: call_scene("controls")),
            ("CREDITS", lambda: call_scene("credits")),
            ("QUIT", lambda: call_scene("quit"))
        ], min_width=25, selected_style=curses.A_BOLD)

        _watch_keys(menu)


@register_scene("options")
class OptionsScene(Scene):
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx("HERE GO THE OPTIONS!", vertical=0.5, horizontal=0.5)
        screen.display("HERE GO THE OPTIONS!", center_y, center_x, util.ColorPair.TITLE.pair)

        _watch_keys([])


@register_scene("controls")
class ControlsScene(Scene):
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx("HERE GO THE CONTROLS!", vertical=0.5, horizontal=0.5)
        screen.display("HERE GO THE CONTROLS!", center_y, center_x, util.ColorPair.TITLE.pair)

        _watch_keys([])


@register_scene("credits")
class CreditsScene(Scene):
    def display(self) -> None:
        screen.clear()

        text = "Credits"
        screen.display(text, *screen.positionyx(text, vertical=0.4, horizontal=0.5),
                       util.ColorPair.SUCCESS.pair)

        text = "Ziyad Edher"
        screen.display(text, *screen.positionyx(text, vertical=0.5, horizontal=0.5),
                       util.ColorPair.STANDARD.pair)

        _watch_keys([])


@register_scene("quit")
class QuitScene(Scene):
    def display(self) -> None:
        screen.clear()

        text = "Are you sure you want to quit?"
        screen.display(text, *screen.positionyx(text, vertical=0.4, horizontal=0.5),
                       util.ColorPair.WARNING.pair)

        assert can_go_back()
        menu = _generate_menu([
            ("NO", go_back),
            ("YES", SceneManager.quit),
        ], min_width=10, selected_style=curses.A_BOLD)

        _watch_keys(menu)


def _generate_menu(options: List[Tuple[str, Callable[[], Any]]], spacing: int = 2, min_width: int = 0,
                   selected_style=curses.A_STANDOUT) -> List[Tuple[str, int, str, Callable[[], Any]]]:
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
                               util.ColorPair.SELECTED.pair | selected_style if self.selection == i else curses.A_NORMAL)

    menu = Menu([option[1] for option in options])
    menu.update()
    return [
        ("up", curses.KEY_UP, "select above", menu.up),
        ("down", curses.KEY_DOWN, "select below", menu.down),
        ("enter", 10, "select", menu.select)
    ]


def _watch_keys(options: List[Tuple[str, int, str, Callable[[], Any]]], joiner: str = "    ",
                show_keys: bool = True, callback: Callable[[int], Any] = lambda i: None) -> None:
    """Watch the keys given by <options> which describes a list of tuples of the form
    ("key name", keycode, "action name", action). These keys will be displayed at the bottom of the screen if
    <show_keys> is True, and a <callback> will be called while polling the keys.
    """
    if can_go_back():
        options.append(("backspace", curses.KEY_BACKSPACE, "back", go_back))

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
            if key == option[1]:
                screen.nodelay(False)
                option[3]()
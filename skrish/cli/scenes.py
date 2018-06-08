"""Manages certain pre-made scenes for the interface.
"""
import curses
from typing import Tuple, List, Callable, Dict, Iterable

from skrish.cli import util
from skrish.cli.cli import Interface


interface = Interface.instance
screen = interface.screen
game = Interface.instance.game

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


class NoSuchSceneException(Exception):
    pass


class Scene:
    """Abstract scene class.
    """
    name: str

    def display(self) -> None:
        """Construct and display the scene.
        """
        raise NotImplementedError


__scenes_list: Dict[str, Callable[[], Scene]] = {}


def call_scene(identifier: str) -> None:
    """Call the scene with the given identifier.

    Raises a `NoSuchSceneException` if there does not exist a scene with the given identifier.
    """
    if identifier not in __scenes_list:
        raise NoSuchSceneException("This scene does not exist.")
    __scenes_list[identifier]().display()


def get_scene_identifiers() -> Iterable[str]:
    """Get the identifiers of all registered scenes.
    """
    return __scenes_list.keys()


def __register_scene(identifier: str) -> Callable[[Callable[[], Scene]], Callable[[], Scene]]:
    def decorator(cls: Callable[[], Scene]) -> Callable[[], Scene]:
        __scenes_list[identifier] = cls
        return cls
    return decorator


@__register_scene("intro")
class IntroScene(Scene):
    """Introduction scene.
    """
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx(TITLE, vertical=0.5, horizontal=0.5)
        start = -max(len(line) for line in TITLE.split("\n"))
        screen.scroll_message(TITLE, 2, center_y - 10, start, center_y - 10, center_x,
                              util.ColorPair.TITLE.pair, skippable=True)


@__register_scene("main_menu")
class MainMenuScene(Scene):
    """Main menu scene.
    """
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx(TITLE, vertical=0.5, horizontal=0.5)
        screen.display(TITLE, center_y - 10, center_x, util.ColorPair.TITLE.pair)

        _generate_menu([("START", lambda: None),
                         ("OPTIONS", lambda: None),
                         ("CREDITS", lambda: None),
                         ("QUIT", lambda: None)],
                        spacing=2, min_width=25, selected_style=curses.A_BOLD)


def _generate_menu(options: List[Tuple[str, callable]],
                    spacing: int = 2, min_width: int = 0, selected_style=curses.A_STANDOUT) -> None:
    """Generate a menu with the given options.
    """
    screen.nodelay(True)

    selection = -1
    num_selections = len(options)
    width = max(min_width, max(len(option[0]) for option in options))

    while True:
        key = screen.getch()
        if selection == -1:
            selection = 0
            key = 1

        if key == 10:  # chr(10) == "\n"
            break
        if key == curses.KEY_UP:
            selection -= 1
            selection %= num_selections
        if key == curses.KEY_DOWN:
            selection += 1
            selection %= num_selections
        if key <= 0:
            continue

        for i, option in enumerate(options):
            message = option[0]
            message = "[ " + message.center(width) + " ]"
            center_y, center_x = screen.positionyx(message, vertical=0.5, horizontal=0.5)
            screen.display(message, center_y + i * spacing, center_x,
                                  util.ColorPair.SELECTED.pair | selected_style if selection == i else curses.A_NORMAL)

    options[selection][1]()  # Call the option's action

    screen.nodelay(False)


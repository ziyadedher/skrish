"""Contains pre-made scenes for the interface.
"""
import curses
from typing import Tuple, List

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
go_back = SceneManager.go_back


BACK_KEY = curses.KEY_BACKSPACE


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

        _generate_menu([("START", lambda: None),
                         ("OPTIONS", lambda: call_scene("options")),
                         ("CONTROLS", lambda: call_scene("controls")),
                         ("CREDITS", lambda: call_scene("credits")),
                         ("QUIT", lambda: call_scene("quit"))],
                       spacing=2, min_width=25, selected_style=curses.A_BOLD)


@register_scene("options")
class OptionsScene(Scene):
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx("HERE GO THE OPTIONS!", vertical=0.5, horizontal=0.5)
        screen.display("HERE GO THE OPTIONS!", center_y, center_x, util.ColorPair.TITLE.pair)

        key = -1
        while key != BACK_KEY:
            pass
            key = screen.getch()
        go_back()


@register_scene("controls")
class ControlsScene(Scene):
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx("HERE GO THE CONTROLS!", vertical=0.5, horizontal=0.5)
        screen.display("HERE GO THE CONTROLS!", center_y, center_x, util.ColorPair.TITLE.pair)

        key = -1
        while key != BACK_KEY:
            pass
            key = screen.getch()
        go_back()


@register_scene("credits")
class CreditsScene(Scene):
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx("HERE GO THE CREDITS!", vertical=0.5, horizontal=0.5)
        screen.display("HERE GO THE CREDITS!", center_y, center_x, util.ColorPair.TITLE.pair)

        key = -1
        while key != BACK_KEY:
            pass
            key = screen.getch()
        go_back()


@register_scene("quit")
class QuitScene(Scene):
    def display(self) -> None:
        screen.clear()

        center_y, center_x = screen.positionyx("HERE GO THE QUIT!", vertical=0.5, horizontal=0.5)
        screen.display("HERE GO THE QUIT!", center_y, center_x, util.ColorPair.TITLE.pair)

        key = -1
        while key != BACK_KEY:
            pass
            key = screen.getch()
        go_back()


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

    screen.nodelay(False)
    options[selection][1]()  # Call the option's action
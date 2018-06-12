"""Contains pre-made scenes for the interface.
"""
import curses
from typing import Callable, Tuple, Optional

from skrish.cli.elements import ElementContainer, BasicTextElement, MenuElement, Element, SpinnerElement
from skrish.cli.util import Anchor, ColorPair
from skrish.cli.scene_manager import Scene, SceneControl, SceneManager
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
get_scene = SceneManager.get_scene
can_go_back = SceneManager.can_go_back


@register_scene("intro")
class IntroScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    def display(self) -> Tuple[Optional[Scene], SceneControl]:
        screen.clear()

        intro = BasicTextElement(screen, 0.3, -0.2, TITLE, style=ColorPair.TITLE.pair)
        intro.move(1, horizontal=0.7, skippable=True)

        return _scene_goto("main_menu")


@register_scene("main_menu")
class MainMenuScene(Scene):
    menu: MenuElement

    def __init__(self) -> None:
        super().__init__()

        self.menu = MenuElement(screen, 0.5, 0.5, [
            ("START", lambda: _scene_goto("character_creation", remove_history=True), True),
            ("OPTIONS", lambda: _scene_goto("options"), True),
            ("CREDITS", lambda: _scene_goto("credits"), True),
            ("QUIT", self.ask_quit, True)
        ], min_width=25, selected_style=curses.A_STANDOUT | curses.A_BOLD)
        self.element_container.add_element("menu", self.menu)

        self.title = BasicTextElement(screen, 0.3, 0.5, TITLE, style=ColorPair.TITLE.pair)
        self.element_container.add_element("title", self.title)

    def display(self) -> Tuple[Optional[Scene], SceneControl]:
        screen.clear()

        self.element_container.display()

        return screen.watch_keys(self.menu.get_standard_keybinds())()

    @staticmethod
    def ask_quit() -> Callable[[], Tuple[Optional[Scene], SceneControl]]:
        quit_screen = screen.dialogue(0.5, 0.5, 0.5, 0.5)

        BasicTextElement(quit_screen, 0.25, 0.5, "=== QUIT ===", style=curses.A_BOLD).display()
        BasicTextElement(quit_screen, 0.4, 0.5, "Are you sure you want to quit?", style=ColorPair.WARNING.pair).display()

        menu = MenuElement(quit_screen, 0.5, 0.5, [
            ("NO", lambda: _scene_goto("NOOP"), True),
            ("YES", lambda: _scene_goto("EXIT"), True),
        ], min_width=10, initial_selection=0)
        menu.display()

        return quit_screen.watch_keys(menu.get_standard_keybinds() + _close_dialogue(), listener_screen=screen)()


@register_scene("options")
class OptionsScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.element_container["title"] = BasicTextElement(screen, 0.25, 0.5, "=== OPTIONS ===", style=curses.A_BOLD)

    def display(self) -> Tuple[Optional[Scene], SceneControl]:
        screen.clear()

        self.element_container.display()

        return screen.watch_keys(_back_if_possible())()


@register_scene("credits")
class CreditsScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.element_container["title"] = BasicTextElement(screen, 0.25, 0.5, "=== CREDITS ===", style=curses.A_BOLD)

    def display(self) -> Tuple[Optional[Scene], SceneControl]:
        screen.clear()

        self.element_container.display()

        return screen.watch_keys(_back_if_possible())()


@register_scene("character_creation")
class CharacterCreationScene(Scene):
    character: Screen
    info: Screen
    controls: Screen

    def __init__(self) -> None:
        super().__init__()

        self.character, self.info, self.controls = screen.grid_screen([
            (0.75, 1, 0, 0),
            (0.25, 0.75, 0.75, 0.25),
            (0.25, 0.25, 0.75, 0)
        ])

        spinners = [
            SpinnerElement(screen, 0, 0, 1, min_value=0, max_value=50, initial_value=10, label="Strength"),
            SpinnerElement(screen, 0, 0, 1, min_value=0, max_value=50, initial_value=10, label="Attack"),
            SpinnerElement(screen, 0, 0, 1, min_value=0, max_value=50, initial_value=10, label="Defence"),
            SpinnerElement(screen, 0, 0, 1, min_value=0, max_value=50, initial_value=10, label="Agility"),
            SpinnerElement(screen, 0, 0, 1, min_value=0, max_value=50, initial_value=10, label="Intelligence")
        ]
        self.menu = MenuElement(self.character, 0, 0, [
            (spinners[0], spinners[0].generate_selected_method(screen), False),
            (spinners[1], spinners[1].generate_selected_method(screen), False),
            (spinners[2], spinners[2].generate_selected_method(screen), False),
            (spinners[3], spinners[3].generate_selected_method(screen), False),
            (spinners[4], spinners[4].generate_selected_method(screen), False)
        ], anchor=Anchor.TOP_LEFT, offset=(5, 5), edges=("", ""))
        self.element_container["character_stats_menu"] = self.menu

        self.element_container["character_title"] = \
            BasicTextElement(self.character, 0, 0, " Character Creation ",
                             anchor=Anchor.TOP_LEFT, offset=(0, 2), style=curses.A_BOLD)
        self.element_container["info_title"] = \
            BasicTextElement(self.info, 0, 0, " Info ",
                             anchor=Anchor.TOP_LEFT, offset=(0, 2), style=curses.A_BOLD)
        self.element_container["controls_title"] = \
            BasicTextElement(self.controls, 0, 0, " Controls ",
                             anchor=Anchor.TOP_LEFT, offset=(0, 2), style=curses.A_BOLD)

    def display(self) -> Tuple[Optional[Scene], SceneControl]:
        screen.clear()

        self.character.box()
        self.info.box()
        self.controls.box()

        self.element_container.display()

        return self.controls.watch_keys(
            self.menu.get_standard_keybinds() + [
                ("backspace", [curses.KEY_BACKSPACE, 127], "main menu", self.ask_main_menu, True)
            ],
            vertical=0, horizontal=0, joiner="\n", anchor=Anchor.TOP_LEFT, offset=(1, 1),
            listener_screen=screen
        )()

    @staticmethod
    def ask_main_menu() -> Callable[[], Tuple[Optional[Scene], SceneControl]]:
        sure = screen.dialogue(0.5, 0.5, 0.4, 0.5)

        BasicTextElement(sure, 0.25, 0.5, "=== MAIN MENU ===", style=curses.A_BOLD).display()
        BasicTextElement(sure, 0.4, 0.5,
                         "Are you sure you want to go back to the main menu and discard your character?",
                         style=ColorPair.WARNING.pair).display()

        menu = MenuElement(sure, 0.5, 0.5, [
            ("NO", lambda: _scene_goto("NOOP"), True),
            ("YES", lambda: _scene_goto("EXIT"), True),
        ], min_width=10, initial_selection=0)
        menu.display()

        return sure.watch_keys(menu.get_standard_keybinds() + _close_dialogue(), listener_screen=screen)()


def _scene_goto(identifier: str, remove_history: bool = False) -> Tuple[Scene, SceneControl]:
    """Goto the scene with the given <identifier> or `back` to go back. Can also <remove_history>.
    """
    scene = None
    if identifier == "BACK":
        control = SceneControl.BACK
    elif identifier == "NOOP":
        control = SceneControl.STAY
    elif identifier == "EXIT":
        control = SceneControl.GOTO
    else:
        scene = SceneManager.get_scene(identifier)()
        control = SceneControl.GOTO

    if remove_history:
        control = SceneControl.REMOVE_HISTORY

    return scene, control


def _back_if_possible():
    """Return a unified back key if possible.
    """
    if not can_go_back():
        return []
    return [("backspace", [curses.KEY_BACKSPACE, 127], "go back", lambda: _scene_goto("BACK"), True)]


def _close_dialogue():
    """Return a unified close dialogue key.
    """
    return [("backspace", [curses.KEY_BACKSPACE, 127], "go back", lambda: _scene_goto("NOOP"), True)]

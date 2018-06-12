"""Contains pre-made scenes for the interface.
"""
import curses
from typing import Callable, Tuple, Optional

from skrish.cli.elements import ElementContainer, BasicTextElement
from skrish.cli import util
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
        pass

    def display(self) -> Tuple[Optional[Scene], SceneControl]:
        screen.clear()

        intro = BasicTextElement(screen, 0.3, -0.2, TITLE)
        intro.move(2, horizontal=0.7, skippable=True)

        return get_scene("main_menu")(), SceneControl.GOTO


# @register_scene("main_menu")
# class MainMenuScene(Scene):
#     def __init__(self) -> None:
#         self.menu = util.Menu(screen, [
#             ("START", lambda: _scene_goto("character_creation", remove_history=True), True),
#             ("OPTIONS", lambda: _scene_goto("options"), True),
#             ("CREDITS", lambda: _scene_goto("credits"), True),
#             ("QUIT", self.ask_quit, True)
#         ], min_width=25, selected_style=curses.A_BOLD)
#
#     def display(self) -> Tuple[Optional[Scene], SceneControl]:
#         screen.clear()
#
#         screen.put(TITLE, 0.3, 0.5, util.ColorPair.TITLE.pair)
#
#         self.menu.update()
#
#         return screen.watch_keys(self.menu.get_standard_keybinds())()
#
#     @staticmethod
#     def ask_quit() -> Callable[[], Tuple[Optional[Scene], SceneControl]]:
#         quit_screen = screen.dialogue(0.5, 0.5, 0.5, 0.5)
#
#         quit_screen.put("=== QUIT ===", 0.25, 0.5, curses.A_BOLD, anchor=util.Anchor.CENTER_CENTER)
#
#         text = "Are you sure you want to quit?"
#         quit_screen.put(text, 0.4, 0.5,
#                         util.ColorPair.WARNING.pair)
#
#         menu = util.Menu(quit_screen, [
#             ("NO", lambda: _scene_goto("NOOP"), True),
#             ("YES", lambda: _scene_goto("EXIT"), True),
#         ], min_width=10, selected_style=curses.A_BOLD)
#
#         return quit_screen.watch_keys(menu.get_standard_keybinds() + _close_dialogue(), listener_screen=screen)()
#
#
# @register_scene("options")
# class OptionsScene(Scene):
#     def display(self) -> Tuple[Optional[Scene], SceneControl]:
#         screen.clear()
#
#         screen.put("=== OPTIONS ===", 0.25, 0.5, curses.A_BOLD, anchor=util.Anchor.CENTER_CENTER)
#
#         return screen.watch_keys(_back_if_possible())()
#
#
# @register_scene("credits")
# class CreditsScene(Scene):
#     def display(self) -> Tuple[Optional[Scene], SceneControl]:
#         screen.clear()
#
#         screen.put("=== CREDITS ===", 0.25, 0.5, curses.A_BOLD, anchor=util.Anchor.CENTER_CENTER)
#
#         text = "Ziyad Edher"
#         screen.put(text, 0.5, 0.5, util.ColorPair.STANDARD.pair)
#
#         return screen.watch_keys(_back_if_possible())()
#
#
# @register_scene("character_creation")
# class CharacterCreationScene(Scene):
#     def __init__(self) -> None:
#         # Screen grid setup
#         self.character, self.info, self.controls = screen.grid_screen([
#             (0.75, 1, 0, 0),
#             (0.25, 0.75, 0.75, 0.25),
#             (0.25, 0.25, 0.75, 0)
#         ])
#
#         self.spinners = [
#             util.Spinner(self.character, 0, 10, 50, 1),
#             util.Spinner(self.character, 0, 10, 50, 1),
#             util.Spinner(self.character, 0, 10, 50, 1),
#             util.Spinner(self.character, 0, 10, 50, 1),
#             util.Spinner(self.character, 0, 10, 50, 1)
#         ]
#
#         self.menu = util.Menu(self.character, [
#             ("Strength", self.spinners[0].generate_selected_method(self.controls, screen), False),
#             ("Attack", self.spinners[1].generate_selected_method(self.controls, screen), False),
#             ("Defence", self.spinners[2].generate_selected_method(self.controls, screen), False),
#             ("Intelligence", self.spinners[3].generate_selected_method(self.controls, screen), False),
#             ("Agility", self.spinners[4].generate_selected_method(self.controls, screen), False)
#         ], vertical=0, horizontal=0, anchor=util.Anchor.TOP_LEFT, offset=(5, 5))
#
#         self.menu.attach_spinners(self.spinners, 0.1)
#
#     def display(self) -> Tuple[Optional[Scene], SceneControl]:
#         screen.clear()
#
#         self.character.box()
#         self.info.box()
#         self.controls.box()
#
#         self.character.put(" Character Creation ", 0, 0, curses.A_BOLD, anchor=util.Anchor.TOP_LEFT, offset=(0, 1))
#         self.info.put(" Info ", 0, 0, curses.A_BOLD, anchor=util.Anchor.TOP_LEFT, offset=(0, 1))
#         self.controls.put(" Controls ", 0, 0, curses.A_BOLD, anchor=util.Anchor.TOP_LEFT, offset=(0, 1))
#
#         for spinner in self.spinners:
#             spinner.update()
#         self.menu.update()
#
#         return self.controls.watch_keys(
#             self.menu.get_standard_keybinds() + [
#                 ("backspace", [curses.KEY_BACKSPACE, 127], "main menu", self.ask_main_menu, True)
#             ],
#             vertical=0, horizontal=0, joiner="\n", anchor=util.Anchor.TOP_LEFT, offset=(1, 1),
#             listener_screen=screen
#         )()
#
#     @staticmethod
#     def ask_main_menu() -> Callable[[], Tuple[Optional[Scene], SceneControl]]:
#         sure = screen.dialogue(0.3, 0.5, 0.5, 0.5)
#
#         sure.put("=== MAIN MENU ===", 0.25, 0.5, curses.A_BOLD, anchor=util.Anchor.CENTER_CENTER)
#
#         text = "Are you sure you want to return to the main menu and discard your character?"
#         sure.put(text, 0.4, 0.5,
#                  util.ColorPair.WARNING.pair)
#
#         menu = util.Menu(sure, [
#             ("NO", lambda: _scene_goto("NOOP"), True),
#             ("YES", lambda: _scene_goto("main_menu"), True),
#         ], min_width=10, selected_style=curses.A_BOLD)
#
#         return sure.watch_keys(menu.get_standard_keybinds() + _close_dialogue(), listener_screen=screen, vertical=0.8)()
#
#
# def _scene_goto(identifier: str, remove_history: bool = False) -> Tuple[Scene, SceneControl]:
#     """Goto the scene with the given <identifier> or `back` to go back. Can also <remove_history>.
#     """
#     if identifier == "BACK":
#         scene = None
#         control = SceneControl.BACK
#     elif identifier == "NOOP":
#         scene = None
#         control = SceneControl.STAY
#     elif identifier == "EXIT":
#         scene = None
#         control = SceneControl.GOTO
#     else:
#         scene = SceneManager.get_scene(identifier)()
#         control = SceneControl.GOTO
#
#     if remove_history:
#         control = SceneControl.REMOVE_HISTORY
#
#     return scene, control
#
#
# def _back_if_possible():
#     """Return a unified back key if possible.
#     """
#     if not can_go_back():
#         return []
#     return [("backspace", [curses.KEY_BACKSPACE, 127], "go back", lambda: _scene_goto("BACK"), True)]
#
#
# def _close_dialogue():
#     """Return a unified close dialogue key.
#     """
#     return [("backspace", [curses.KEY_BACKSPACE, 127], "go back", lambda: _scene_goto("NOOP"), True)]

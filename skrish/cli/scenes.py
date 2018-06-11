"""Contains pre-made scenes for the interface.
"""
import curses

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
        screen.scroll_message(TITLE, 2, 0.3, -0.2, 0.3, 0.5, util.ColorPair.TITLE.pair, skippable=True)


@register_scene("main_menu")
class MainMenuScene(Scene):
    def display(self) -> None:
        screen.clear()

        screen.put(TITLE, 0.3, 0.5, util.ColorPair.TITLE.pair)

        menu = screen.generate_menu([
            ("START", lambda: call_scene("character_creation")),
            ("OPTIONS", lambda: call_scene("options")),
            ("CREDITS", lambda: call_scene("credits")),
            ("QUIT", lambda: call_scene("quit"))
        ], min_width=25, selected_style=curses.A_BOLD)

        screen.watch_keys(options=menu)


@register_scene("options")
class OptionsScene(Scene):
    def display(self) -> None:
        screen.clear()

        screen.put("=== OPTIONS ===", 0.25, 0.5, curses.A_BOLD, anchor=util.Anchor.CENTER_CENTER)

        screen.watch_keys(_back_if_possible())


@register_scene("credits")
class CreditsScene(Scene):
    def display(self) -> None:
        screen.clear()

        screen.put("=== CREDITS ===", 0.25, 0.5, curses.A_BOLD, anchor=util.Anchor.CENTER_CENTER)

        text = "Ziyad Edher"
        screen.put(text, 0.5, 0.5, util.ColorPair.STANDARD.pair)

        screen.watch_keys(_back_if_possible())


@register_scene("quit")
class QuitScene(Scene):
    def display(self) -> None:
        screen.clear()

        screen.put("=== QUIT ===", 0.25, 0.5, curses.A_BOLD, anchor=util.Anchor.CENTER_CENTER)

        text = "Are you sure you want to quit?"
        screen.put(text, 0.4, 0.5,
                   util.ColorPair.WARNING.pair)

        assert can_go_back()
        menu = screen.generate_menu([
            ("NO", go_back),
            ("YES", SceneManager.quit),
        ], min_width=10, selected_style=curses.A_BOLD)

        screen.watch_keys(menu + _back_if_possible())


@register_scene("character_creation")
class CharacterCreationScene(Scene):
    def display(self) -> None:
        screen.clear()

        # Screen grid setup
        character, log, info, controls = screen.grid_screen([
            (0.75, 0.75, 0, 0),
            (1, 0.25, 0, 0.75),
            (0.25, 0.65, 0.75, 0.1),
            (0.25, 0.1, 0.75, 0)
        ])

        character.box()
        log.box()
        info.box()
        controls.box()

        character.put(" Character Creation ", 0, 0, curses.A_BOLD, anchor=util.Anchor.TOP_LEFT, offset=(0, 1))
        log.put(" Log ", 0, 0, curses.A_BOLD, anchor=util.Anchor.TOP_LEFT, offset=(0, 1))
        info.put(" Info ", 0, 0, curses.A_BOLD, anchor=util.Anchor.TOP_LEFT, offset=(0, 1))
        controls.put(" Controls ", 0, 0, curses.A_BOLD, anchor=util.Anchor.TOP_LEFT, offset=(0, 1))

        controls.watch_keys([
            ("up", [curses.KEY_UP], "select above", lambda: None),
            ("down", [curses.KEY_DOWN], "select below", lambda: None),
            ("left", [curses.KEY_LEFT], "decrement", lambda: None),
            ("right", [curses.KEY_RIGHT], "increment", lambda: None)
        ], vertical=0, horizontal=0, joiner="\n", anchor=util.Anchor.TOP_LEFT, offset=(1, 1))


def _back_if_possible():
    """Return a unified back key if possible.
    """
    if not can_go_back():
        return None
    return [("backspace", [curses.KEY_BACKSPACE, 127], "go back", go_back)]
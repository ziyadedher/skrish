"""Manages certain pre-made scenes for the interface.
"""
import curses
import time
from typing import Tuple, List

from skrish.cli import util
from skrish.cli.screen import Screen

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


class Scener:
    """Contains and executes pre-made scenes.
    """
    __screen: Screen

    def __init__(self, screen: Screen) -> None:
        """Initialize this scener to display on the given <screen>.
        """
        self.__screen = screen

    def intro_sequence(self) -> None:
        """Display the introduction sequence.
        """
        self.__screen.clear()

        center_y, center_x = self.__screen.positionyx(TITLE, vertical=0.5, horizontal=0.5)
        start = -max(len(line) for line in TITLE.split("\n"))
        self.__screen.scroll_message(TITLE, 2, center_y - 10, start, center_y - 10, center_x,
                                     util.ColorPair.TITLE.pair, skippable=True)
        time.sleep(0.1)

    def main_menu(self) -> None:
        self.__screen.clear()

        center_y, center_x = self.__screen.positionyx(TITLE, vertical=0.5, horizontal=0.5)
        self.__screen.display(TITLE, center_y - 10, center_x, util.ColorPair.TITLE.pair)

        self._generate_menu([("START", lambda: None),
                             ("OPTIONS", lambda: None),
                             ("CREDITS", lambda: None),
                             ("QUIT", lambda: None)],
                            spacing=2, min_width=25, selected_style=curses.A_BOLD)

    def _generate_menu(self, options: List[Tuple[str, callable]],
                       spacing: int = 2, min_width: int = 0, selected_style=curses.A_STANDOUT) -> None:
        """Generate a menu with the given options.
        """
        self.__screen.nodelay(True)

        selection = -1
        num_selections = len(options)
        width = max(min_width, max(len(option[0]) for option in options))

        while True:
            key = self.__screen.getch()
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
                center_y, center_x = self.__screen.positionyx(message, vertical=0.5, horizontal=0.5)
                self.__screen.display(message, center_y + i * spacing, center_x,
                                      util.ColorPair.SELECTED.pair | selected_style if selection == i else curses.A_NORMAL)

        options[selection][1]()  # Call the option's action

        self.__screen.nodelay(False)


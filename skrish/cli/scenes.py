"""Manages certain pre-made scenes for the interface.
"""
import curses
import time
from typing import Tuple, List

from skrish.cli import util

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

    def __init__(self, screen) -> None:
        """Initialize this scener to display on the given <screen>.
        """
        self.__screen = screen

    def intro_sequence(self) -> None:
        """Display the introduction sequence.
        """
        self.__screen.clear()

        center_y, center_x = util.centeryx(self.__screen, TITLE, vertical=True, horizontal=True)
        start = -max(len(line) for line in TITLE.split("\n"))
        self.__screen.scroll_message(TITLE, 50, center_y - 10, start, center_y - 10, center_x,
                                     util.ColorPair.TITLE.pair, skippable=True)
        time.sleep(0.1)

    def main_menu(self) -> None:
        self.__screen.clear()

        center_y, center_x = util.centeryx(self.__screen, TITLE, vertical=True, horizontal=True)
        self.__screen.display(TITLE, center_y - 10, center_x, util.ColorPair.TITLE.pair)

        self._generate_menu([("START", lambda: None), ("OPTIONS", lambda: None), ("CREDITS", lambda: None), ("QUIT", lambda: None)],
                            spacing=2, min_width=25)

    def _generate_menu(self, options: List[Tuple[str, callable]], spacing: int = 2, min_width: int = 0) -> None:
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
                message, action = option
                message = "[ " + message.center(width) + " ]"
                center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
                self.__screen.display(message, center_y + i * spacing, center_x, curses.A_UNDERLINE if selection == i else curses.A_NORMAL)

        self.__screen.nodelay(False)


"""Manages certain pre-made scenes for the interface.
"""
import curses
import time

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

        self.__screen.nodelay(True)
        selection = 0

        while True:
            key = self.__screen.getch()

            if key == 10:  # chr(10) == "\n"
                break
            if key == curses.KEY_UP:
                selection -= 1
                selection %= 5
            if key == curses.KEY_DOWN:
                selection += 1
                selection %= 5

            message = "Start"
            center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
            self.__screen.display(message, center_y, center_x, curses.A_UNDERLINE if selection == 0 else curses.A_NORMAL)

            message = "Option 1"
            center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
            self.__screen.display(message, center_y + 2, center_x, curses.A_UNDERLINE if selection == 1 else curses.A_NORMAL)

            message = "Option 2"
            center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
            self.__screen.display(message, center_y + 4, center_x, curses.A_UNDERLINE if selection == 2 else curses.A_NORMAL)

            message = "Option 3"
            center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
            self.__screen.display(message, center_y + 6, center_x, curses.A_UNDERLINE if selection == 3 else curses.A_NORMAL)

            message = "Quit"
            center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
            self.__screen.display(message, center_y + 8, center_x, curses.A_UNDERLINE if selection == 4 else curses.A_NORMAL)

        self.__screen.nodelay(False)
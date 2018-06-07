"""Manages certain pre-made scenes for the interface.
"""
import time

from skrish.cli import util


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

        message = """
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
        center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
        start = -max(len(line) for line in message.split("\n"))
        self.__screen.scroll_message(message, 50, center_y - 10, start, center_y - 10, center_x)

        message = "This is pretty darn cool man."
        center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
        start = -len(message)
        self.__screen.scroll_message(message, 100, center_y, start, center_y, center_x)

        message = "I agree."
        _, x = self.__screen.getyx()
        center_y, center_x = util.centeryx(self.__screen, message, vertical=True, horizontal=True)
        start = -len(message)
        self.__screen.scroll_message(message, 100, center_y + 1, start, center_y + 1, center_x)

        self.__screen.getkey()
"""Provides the entry function to the game.
"""
from skrish.game.game import Game
from skrish.cli import cli


def main():
    """Main entry point to the game.
    """
    # Initialize game
    game = Game()

    # Initialize interface
    with cli.Interface(game) as interface:
        interface = interface.instance
        interface.start()
        interface.call_scene("intro")
        interface.call_scene("main_menu")
        interface.error("Do you know the muffin man?")


if __name__ == '__main__':
    main()
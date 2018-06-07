"""Provides the entry function to the game.
"""
from skrish.cli import cli


def main():
    """Main entry point to the game.
    """
    # Game initialization
    # TODO: initialize game

    # Interface initialization
    with cli.Interface() as interface:
        interface.error("Do you know the muffin man?")


if __name__ == '__main__':
    main()
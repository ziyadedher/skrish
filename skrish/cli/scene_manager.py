"""Manages all interface scenes.
"""
from typing import Iterable, Callable, Dict


class NoSuchSceneException(Exception):
    pass


class Scene:
    """Abstract scene class.
    """
    name: str

    def display(self) -> None:
        """Construct and display the scene.
        """
        raise NotImplementedError


__scenes: Dict[str, Callable[[], Scene]] = {}


def register_scene(identifier: str) -> Callable[[Callable[[], Scene]], Callable[[], Scene]]:
    def decorator(cls: Callable[[], Scene]) -> Callable[[], Scene]:
        __scenes[identifier] = cls
        return cls
    return decorator


def call_scene(identifier: str) -> None:
    """Call the scene with the given identifier.

    Raises a `NoSuchSceneException` if there does not exist a scene with the given identifier.
    """
    if identifier not in __scenes:
        raise NoSuchSceneException("This scene does not exist.")
    __scenes[identifier]().display()


def get_scene_identifiers() -> Iterable[str]:
    """Get the identifiers of all registered scenes.
    """
    return __scenes.keys()

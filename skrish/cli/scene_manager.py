"""Manages all interface scenes.
"""
from typing import Iterable, Callable, Dict, List


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


class SceneManager:
    """Scene manager that organizes, stores, and indexes all scenes.
    """
    __scenes: Dict[str, Callable[[], Scene]] = {}
    __history: List[Scene] = []

    @staticmethod
    def register_scene(identifier: str) -> Callable[[Callable[[], Scene]], Callable[[], Scene]]:
        """Decorator that registers the scene to the given <identifier>.
        """
        def decorator(cls: Callable[[], Scene]) -> Callable[[], Scene]:
            SceneManager.__scenes[identifier] = cls
            return cls
        return decorator

    @staticmethod
    def call_scene(identifier: str, no_back: bool = False) -> None:
        """Call the scene with the given identifier.

        Raises a `NoSuchSceneException` if there does not exist a scene with the given identifier.
        """
        if identifier not in SceneManager.__scenes:
            raise NoSuchSceneException("This scene does not exist.")
        if no_back:
            SceneManager.__history = []

        scene = SceneManager.__scenes[identifier]()
        SceneManager.__history.append(scene)
        scene.display()

    @staticmethod
    def get_scene_identifiers() -> Iterable[str]:
        """Get the identifiers of all registered scenes.
        """
        return SceneManager.__scenes.keys()

    @staticmethod
    def go_back() -> bool:
        """Go back in scene history.
        """
        if not SceneManager.__history:
            return False
        SceneManager.__history.pop()
        SceneManager.__history[-1].display()
        return True
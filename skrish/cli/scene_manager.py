"""Manages all interface scenes.
"""
import sys
from enum import Enum
from typing import Iterable, Callable, Dict, List, Any, Tuple, Optional


class NoSuchSceneException(Exception):
    pass


class SceneControl(Enum):
    REMOVE_HISTORY = -2
    BACK = -1
    STAY = 0
    GOTO = 1

class Scene:
    """Abstract scene class.
    """
    name: str

    def display(self) -> Tuple[Optional['Scene'], int]:
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
        scene = SceneManager.get_scene(identifier)()
        control = SceneControl.REMOVE_HISTORY if no_back else SceneControl.GOTO

        while scene is not None:
            if control == SceneControl.REMOVE_HISTORY:
                SceneManager.__history = []

            past_scene = scene
            scene, control = scene.display()

            if control == SceneControl.BACK:
                scene = SceneManager.__go_back()
                control = SceneControl.GOTO
            elif control == SceneControl.STAY:
                scene = past_scene
            elif control == SceneControl.GOTO:
                SceneManager.__history.append(past_scene)

    @staticmethod
    def get_scene(identifier: str) -> Callable[[], Scene]:
        """Return the scene with the given <identifier>.

        Raises a `NoSuchSceneException` if there does not exist a scene with the given identifier.
        """
        if identifier not in SceneManager.__scenes:
            raise NoSuchSceneException("This scene does not exist.")
        return SceneManager.__scenes[identifier]

    @staticmethod
    def get_scene_identifiers() -> Iterable[str]:
        """Get the identifiers of all registered scenes.
        """
        return SceneManager.__scenes.keys()

    @staticmethod
    def can_go_back() -> bool:
        """Returns whether or not there is scene history.
        """
        return len(SceneManager.__history) > 0

    @staticmethod
    def __go_back() -> Optional[Scene]:
        """Go back in scene history.
        """
        if len(SceneManager.__history) < 2:
            return None
        return SceneManager.__history.pop()

    @staticmethod
    def __quit() -> None:
        """Quit the scene manager.
        """
        sys.exit(0)
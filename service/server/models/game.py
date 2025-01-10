import abc

from codenames.classic.state import ClassicGameState
from codenames.duet.state import DuetGameState
from pydantic import BaseModel


class Game[T: BaseModel](BaseModel, abc.ABC):
    id: str
    state_data: dict

    @classmethod
    @abc.abstractmethod
    def get_state_class(cls) -> type[T]: ...

    @property
    def state(self) -> T:
        return self.get_state_class().model_validate(self.state_data)


class ClassicGame(Game[ClassicGameState]):
    @classmethod
    def get_state_class(cls) -> type[ClassicGameState]:
        return ClassicGameState


class DuetGame(Game[DuetGameState]):
    @classmethod
    def get_state_class(cls) -> type[DuetGameState]:
        return DuetGameState

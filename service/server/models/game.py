from codenames.classic.state import ClassicGameState
from pydantic import BaseModel


class ClassicGame(BaseModel):
    id: str
    state_data: dict

    @property
    def state(self) -> ClassicGameState:
        return ClassicGameState(**self.state_data)

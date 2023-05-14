from codenames.game.state import GameState
from pydantic import BaseModel


class Game(BaseModel):
    id: str
    state_data: dict

    @property
    def state(self) -> GameState:
        return GameState(**self.state_data)

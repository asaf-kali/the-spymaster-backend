from typing import Any, Optional, Union

from codenames.game.move import GivenGuess, GivenHint
from codenames.game.state import GameState
from pydantic import BaseModel, Extra
from the_spymaster_solvers_client.structs.base import ModelIdentifier, Solver


class HttpResponse(BaseModel):
    status_code: int = 200
    headers: Optional[dict] = None
    body: Union[dict, BaseModel]

    @property
    def data(self) -> dict:
        if isinstance(self.body, BaseModel):
            return self.body.dict()
        return self.body


class ErrorResponse(BaseModel):
    message: Optional[str]
    details: Any

    class Config:
        extra = Extra.allow


class StartGameResponse(BaseModel):
    game_id: str
    game_state: GameState


class GetGameStateResponse(BaseModel):
    game_state: GameState


class HintResponse(BaseModel):
    given_hint: GivenHint
    game_state: GameState


class GuessResponse(BaseModel):
    given_guess: Optional[GivenGuess]
    game_state: GameState


class NextMoveResponse(BaseModel):
    game_state: GameState
    used_solver: Solver
    given_hint: Optional[GivenHint]
    given_guess: Optional[GivenGuess]
    used_model_identifier: Optional[ModelIdentifier]

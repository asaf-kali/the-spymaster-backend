from typing import Any, Optional, Union

from codenames.game import GameState, GivenGuess, GivenHint
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
    given_hint: Optional[GivenHint] = None
    given_guess: Optional[GivenGuess] = None
    used_solver: Solver
    used_model_identifier: ModelIdentifier
    game_state: GameState

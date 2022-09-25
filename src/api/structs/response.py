from typing import Any, Optional

from codenames.game import GameState, GivenGuess, GivenHint
from pydantic import BaseModel, Extra
from the_spymaster_solvers_client.structs.base import ModelIdentifier, Solver


class BaseResponse(BaseModel):
    status_code: int = 200


class ErrorResponse(BaseModel):
    message: Optional[str]
    details: Any

    class Config:
        extra = Extra.allow


class StartGameResponse(BaseResponse):
    game_id: str
    game_state: GameState


class GetGameStateResponse(BaseResponse):
    game_state: GameState


class HintResponse(BaseResponse):
    given_hint: GivenHint
    game_state: GameState


class GuessResponse(BaseResponse):
    given_guess: Optional[GivenGuess]
    game_state: GameState


class NextMoveResponse(BaseResponse):
    given_hint: Optional[GivenHint] = None
    given_guess: Optional[GivenGuess] = None
    used_solver: Solver
    used_model_identifier: ModelIdentifier
    game_state: GameState

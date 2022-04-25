from typing import Optional

from codenames.game import GameState, GivenGuess, GivenHint
from codenames.utils.loader.model_loader import ModelIdentifier
from pydantic import BaseModel

from api.models.game import Solver


class BaseResponse(BaseModel):
    status_code: int = 200


class StartGameResponse(BaseResponse):
    game_id: int
    game_state: GameState


class HintResponse(BaseResponse):
    given_hint: GivenHint
    game_state: GameState


class GuessResponse(BaseResponse):
    given_guess: GivenGuess
    game_state: GameState


class GetGameStateResponse(BaseResponse):
    game_state: GameState


class NextMoveResponse(BaseResponse):
    used_solver: Solver
    used_model_identifier: ModelIdentifier
    given_hint: Optional[GivenHint] = None
    given_guess: Optional[GivenGuess] = None
    game_state: GameState
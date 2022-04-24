from codenames.game import GameState, GivenGuess, GivenHint
from pydantic import BaseModel


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

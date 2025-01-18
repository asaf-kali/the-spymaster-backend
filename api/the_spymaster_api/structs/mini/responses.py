from codenames.duet.types import DuetGivenClue, DuetGivenGuess
from codenames.mini.state import MiniGameState
from pydantic import BaseModel
from the_spymaster_solvers_api.structs import APIModelIdentifier, Solver


class MiniStartGameResponse(BaseModel):
    game_id: str
    game_state: MiniGameState


class MiniGetGameStateResponse(BaseModel):
    game_state: MiniGameState


class MiniClueResponse(BaseModel):
    given_clue: DuetGivenClue | None
    game_state: MiniGameState


class MiniGuessResponse(BaseModel):
    given_guess: DuetGivenGuess | None
    game_state: MiniGameState


class MiniNextMoveResponse(BaseModel):
    game_state: MiniGameState
    used_solver: Solver
    given_clue: DuetGivenClue | None = None
    given_guess: DuetGivenGuess | None = None
    used_model_identifier: APIModelIdentifier | None = None

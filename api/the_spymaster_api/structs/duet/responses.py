from codenames.duet.state import DuetGameState
from codenames.duet.types import DuetGivenClue, DuetGivenGuess
from pydantic import BaseModel
from the_spymaster_solvers_api.structs import APIModelIdentifier, Solver


class StartGameResponse(BaseModel):
    game_id: str
    game_state: DuetGameState


class GetGameStateResponse(BaseModel):
    game_state: DuetGameState


class ClueResponse(BaseModel):
    given_clue: DuetGivenClue | None
    game_state: DuetGameState


class GuessResponse(BaseModel):
    given_guess: DuetGivenGuess | None
    game_state: DuetGameState


class NextMoveResponse(BaseModel):
    game_state: DuetGameState
    used_solver: Solver
    given_clue: DuetGivenClue | None = None
    given_guess: DuetGivenGuess | None = None
    used_model_identifier: APIModelIdentifier | None = None

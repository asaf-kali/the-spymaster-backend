from codenames.duet.state import DuetGameState
from codenames.duet.types import DuetGivenClue, DuetGivenGuess
from pydantic import BaseModel
from the_spymaster_solvers_api.structs import APIModelIdentifier, Solver


class DuetStartGameResponse(BaseModel):
    game_id: str
    game_state: DuetGameState


class DuetGetGameStateResponse(BaseModel):
    game_state: DuetGameState


class DuetClueResponse(BaseModel):
    given_clue: DuetGivenClue | None
    game_state: DuetGameState


class DuetGuessResponse(BaseModel):
    given_guess: DuetGivenGuess | None
    game_state: DuetGameState


class DuetNextMoveResponse(BaseModel):
    game_state: DuetGameState
    used_solver: Solver
    given_clue: DuetGivenClue | None = None
    given_guess: DuetGivenGuess | None = None
    used_model_identifier: APIModelIdentifier | None = None

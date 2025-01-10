from typing import Optional

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
    given_guess: Optional[DuetGivenGuess]
    game_state: DuetGameState


class NextMoveResponse(BaseModel):
    game_state: DuetGameState
    used_solver: Solver
    given_clue: Optional[DuetGivenClue] = None
    given_guess: Optional[DuetGivenGuess] = None
    used_model_identifier: Optional[APIModelIdentifier]

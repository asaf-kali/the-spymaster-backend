from typing import Optional

from codenames.classic.state import ClassicGameState
from codenames.classic.team import ClassicTeam
from codenames.classic.types import ClassicGivenClue, ClassicGivenGuess
from codenames.generic.move import GivenClue, GivenGuess
from pydantic import BaseModel
from the_spymaster_solvers_api.structs import APIModelIdentifier, Solver


class StartGameResponse(BaseModel):
    game_id: str
    game_state: ClassicGameState


class GetGameStateResponse(BaseModel):
    game_state: ClassicGameState


class ClueResponse(BaseModel):
    given_clue: GivenClue[ClassicTeam] | None
    game_state: ClassicGameState


class GuessResponse(BaseModel):
    given_guess: Optional[GivenGuess]
    game_state: ClassicGameState


class NextMoveResponse(BaseModel):
    game_state: ClassicGameState
    used_solver: Solver
    given_clue: Optional[ClassicGivenClue] = None
    given_guess: Optional[ClassicGivenGuess] = None
    used_model_identifier: Optional[APIModelIdentifier]

from codenames.classic.state import ClassicGameState
from codenames.classic.types import ClassicGivenClue, ClassicGivenGuess
from pydantic import BaseModel
from the_spymaster_solvers_api.structs import APIModelIdentifier, Solver


class StartGameResponse(BaseModel):
    game_id: str
    game_state: ClassicGameState


class GetGameStateResponse(BaseModel):
    game_state: ClassicGameState


class ClueResponse(BaseModel):
    given_clue: ClassicGivenClue | None
    game_state: ClassicGameState


class GuessResponse(BaseModel):
    given_guess: ClassicGivenGuess | None
    game_state: ClassicGameState


class NextMoveResponse(BaseModel):
    game_state: ClassicGameState
    used_solver: Solver
    given_clue: ClassicGivenClue | None = None
    given_guess: ClassicGivenGuess | None = None
    used_model_identifier: APIModelIdentifier | None = None

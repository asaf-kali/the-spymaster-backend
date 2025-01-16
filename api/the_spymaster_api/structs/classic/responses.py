from codenames.classic.state import ClassicGameState
from codenames.classic.types import ClassicGivenClue, ClassicGivenGuess
from pydantic import BaseModel
from the_spymaster_solvers_api.structs import APIModelIdentifier, Solver


class ClassicStartGameResponse(BaseModel):
    game_id: str
    game_state: ClassicGameState


class ClassicGetGameStateResponse(BaseModel):
    game_state: ClassicGameState


class ClassicClueResponse(BaseModel):
    given_clue: ClassicGivenClue | None
    game_state: ClassicGameState


class ClassicGuessResponse(BaseModel):
    given_guess: ClassicGivenGuess | None
    game_state: ClassicGameState


class ClassicNextMoveResponse(BaseModel):
    game_state: ClassicGameState
    used_solver: Solver
    given_clue: ClassicGivenClue | None = None
    given_guess: ClassicGivenGuess | None = None
    used_model_identifier: APIModelIdentifier | None = None

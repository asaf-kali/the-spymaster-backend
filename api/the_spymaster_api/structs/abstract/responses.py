from pydantic import BaseModel
from the_spymaster_solvers_api.structs import APIModelIdentifier, Solver


class StartGameResponse[StateType](BaseModel):
    game_id: str
    game_state: StateType


class GetGameStateResponse[StateType](BaseModel):
    game_state: StateType


class ClueResponse[StateType, ClueType](BaseModel):
    given_clue: ClueType | None
    game_state: StateType


class GuessResponse[StateType, GuessType](BaseModel):
    given_guess: GuessType | None
    game_state: StateType


class NextMoveResponse[StateType, ClueType, GuessType](BaseModel):
    game_state: StateType
    used_solver: Solver
    given_clue: ClueType | None = None
    given_guess: GuessType | None = None
    used_model_identifier: APIModelIdentifier | None = None

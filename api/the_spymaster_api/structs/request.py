from typing import List, Optional

from pydantic import BaseModel, Extra
from the_spymaster_solvers_client.structs.base import ModelIdentifier, Solver


class BaseRequest(BaseModel):
    class Config:
        extra = Extra.allow
        fields = {"drf_request": {"exclude": True}}
        arbitrary_types_allowed = True

    @property
    def preforming_user(self):
        drf_request = getattr(self, "drf_request", None)
        return drf_request.user if drf_request else None


class StartGameRequest(BaseRequest):
    language: str = "english"


class HintRequest(BaseRequest):
    game_id: str
    word: str
    card_amount: int
    for_words: Optional[List[str]] = None


class GuessRequest(BaseRequest):
    game_id: str
    card_index: int


class GetGameStateRequest(BaseRequest):
    game_id: str


class NextMoveRequest(BaseRequest):
    game_id: str
    solver: Solver = Solver.NAIVE
    model_identifier: Optional[ModelIdentifier] = None

from typing import List, Optional

from pydantic import BaseModel
from the_spymaster_solvers_api.structs.base import APIModelIdentifier, Solver


class BaseRequest(BaseModel):
    class Config:
        extra = "allow"
        fields = {"drf_request": {"exclude": True}}
        arbitrary_types_allowed = True

    @property
    def preforming_user(self):
        drf_request = getattr(self, "drf_request", None)
        return drf_request.user if drf_request else None


class ClueRequest(BaseRequest):
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
    model_identifier: APIModelIdentifier | None = None

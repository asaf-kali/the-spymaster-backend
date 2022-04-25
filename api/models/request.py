from typing import List, Optional

from codenames.utils.loader.model_loader import ModelIdentifier
from pydantic import BaseModel
from rest_framework.request import Request

from api.models import SpymasterUser
from api.models.game import Solver


class BaseRequest(BaseModel):
    drf_request: Request

    class Config:
        fields = {"drf_request": {"exclude": True}}
        arbitrary_types_allowed = True

    @property
    def preforming_user(self) -> SpymasterUser:
        return self.drf_request.user


class StartGameRequest(BaseRequest):
    language: str = "english"


class HintRequest(BaseRequest):
    game_id: int
    word: str
    card_amount: int
    for_words: List[str] = None


class GuessRequest(BaseRequest):
    game_id: int
    card_index: int


class GetGameStateRequest(BaseRequest):
    game_id: int


class NextMoveRequest(BaseRequest):
    game_id: int
    model_identifier: Optional[ModelIdentifier] = None
    solver: Solver = Solver.NAIVE

from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel
from rest_framework.request import Request
from solvers.models import ModelIdentifier

if TYPE_CHECKING:
    from api.models import SpymasterUser

from api.structs import Solver


class BaseRequest(BaseModel):
    drf_request: Optional[Request] = None

    class Config:
        fields = {"drf_request": {"exclude": True}}
        arbitrary_types_allowed = True

    @property
    def preforming_user(self) -> Optional["SpymasterUser"]:
        if not self.drf_request:
            return None
        return self.drf_request.user


class StartGameRequest(BaseRequest):
    language: str = "english"


class HintRequest(BaseRequest):
    game_id: int
    word: str
    card_amount: int
    for_words: Optional[List[str]] = None


class GuessRequest(BaseRequest):
    game_id: int
    card_index: int


class GetGameStateRequest(BaseRequest):
    game_id: int


class NextMoveRequest(BaseRequest):
    game_id: int
    model_identifier: Optional[ModelIdentifier] = None
    solver: Solver = Solver.NAIVE


class LoadModelsRequest(BaseRequest):
    model_identifiers: List[ModelIdentifier] = []

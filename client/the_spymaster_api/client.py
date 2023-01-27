import logging
from typing import Optional

from the_spymaster_solvers_client.structs.requests import LoadModelsRequest
from the_spymaster_solvers_client.structs.responses import LoadModelsResponse
from the_spymaster_util.http.base_client import DEFAULT_RETRY_STRATEGY, BaseHttpClient
from urllib3 import Retry

from .structs import (
    GetGameStateRequest,
    GetGameStateResponse,
    GuessRequest,
    GuessResponse,
    HintRequest,
    HintResponse,
    NextMoveRequest,
    NextMoveResponse,
    StartGameRequest,
    StartGameResponse,
)
from .structs.errors import SERVICE_ERRORS

log = logging.getLogger(__name__)
DEFAULT_BASE_URL = "http://localhost:8000"


class TheSpymasterClient(BaseHttpClient):
    def __init__(self, base_url: Optional[str] = None, retry_strategy: Optional[Retry] = DEFAULT_RETRY_STRATEGY):
        if not base_url:
            base_url = DEFAULT_BASE_URL
        super().__init__(
            base_url=f"{base_url}/api/v1/game", retry_strategy=retry_strategy, common_errors=SERVICE_ERRORS
        )

    def start_game(self, request: StartGameRequest) -> StartGameResponse:
        data = self.post(endpoint="start/", data=request.dict(), error_types={})
        return StartGameResponse(**data)

    def hint(self, request: HintRequest) -> HintResponse:
        data = self.post(endpoint="hint/", data=request.dict())
        return HintResponse(**data)

    def guess(self, request: GuessRequest) -> GuessResponse:
        data = self.post(endpoint="guess/", data=request.dict())
        return GuessResponse(**data)

    def next_move(self, request: NextMoveRequest) -> NextMoveResponse:
        data = self.post(endpoint="next-move/", data=request.dict())
        return NextMoveResponse(**data)

    def get_game_state(self, request: GetGameStateRequest) -> GetGameStateResponse:
        data = self.get(endpoint="state/", data=request.dict())
        return GetGameStateResponse(**data)

    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        data = self.post(endpoint="load-models/", data=request.dict())
        return LoadModelsResponse(**data)

    def raise_error(self, request: dict):
        return self.get(endpoint="raise-error/", data=request)

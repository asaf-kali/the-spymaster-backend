import logging

from the_spymaster_solvers_client.structs.requests import LoadModelsRequest
from the_spymaster_solvers_client.structs.responses import LoadModelsResponse
from the_spymaster_util import wrap
from the_spymaster_util.http_client import BaseHttpClient

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

log = logging.getLogger(__name__)
DEFAULT_BASE_URL = "http://localhost:8000"


class TheSpymasterClient(BaseHttpClient):
    def __init__(self, base_url: str = None):
        if not base_url:
            base_url = DEFAULT_BASE_URL
        super().__init__(base_url=f"{base_url}/api/v1/game")
        log.debug(f"Backend client using base url: {wrap(self.base_url)}")

    def start_game(self, request: StartGameRequest) -> StartGameResponse:
        data = self._post("start/", data=request.dict())
        return StartGameResponse(**data)

    def hint(self, request: HintRequest) -> HintResponse:
        data = self._post("hint/", data=request.dict())
        return HintResponse(**data)

    def guess(self, request: GuessRequest) -> GuessResponse:
        data = self._post("guess/", data=request.dict())
        return GuessResponse(**data)

    def next_move(self, request: NextMoveRequest) -> NextMoveResponse:
        data = self._post("next-move/", data=request.dict())
        return NextMoveResponse(**data)

    def get_game_state(self, request: GetGameStateRequest) -> GetGameStateResponse:
        data = self._get("state/", data=request.dict())
        return GetGameStateResponse(**data)

    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        data = self._post("async-load-models/", data=request.dict())
        return LoadModelsResponse(**data)

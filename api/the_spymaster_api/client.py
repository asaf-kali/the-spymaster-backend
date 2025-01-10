import logging

from the_spymaster_solvers_api.structs.requests import LoadModelsRequest
from the_spymaster_solvers_api.structs.responses import LoadModelsResponse
from the_spymaster_util.http.base_client import DEFAULT_RETRY_STRATEGY, BaseHttpClient
from urllib3 import Retry

from .structs import (
    SERVICE_ERRORS,
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from .structs.classic.requests import StartGameRequest
from .structs.classic.responses import (
    ClueResponse,
    GetGameStateResponse,
    GuessResponse,
    NextMoveResponse,
    StartGameResponse,
)

log = logging.getLogger(__name__)


class TheSpymasterClient(BaseHttpClient):
    def __init__(self, base_url: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        super().__init__(
            base_url=f"{base_url}/api/v1/game",
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )

    def start_game(self, request: StartGameRequest) -> StartGameResponse:
        data: dict = self.post(endpoint="classic/start/", data=request.model_dump(), error_types={})  # type: ignore
        return StartGameResponse(**data)

    def clue(self, request: ClueRequest) -> ClueResponse:
        data: dict = self.post(endpoint="classic/clue/", data=request.model_dump())  # type: ignore
        return ClueResponse(**data)

    def guess(self, request: GuessRequest) -> GuessResponse:
        data: dict = self.post(endpoint="classic/guess/", data=request.model_dump())  # type: ignore
        return GuessResponse(**data)

    def next_move(self, request: NextMoveRequest) -> NextMoveResponse:
        data: dict = self.post(endpoint="classic/next-move/", data=request.model_dump())  # type: ignore
        return NextMoveResponse(**data)

    def get_game_state(self, request: GetGameStateRequest) -> GetGameStateResponse:
        data: dict = self.get(endpoint="classic/state/", data=request.model_dump())  # type: ignore
        return GetGameStateResponse(**data)

    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        data: dict = self.post(endpoint="load-models/", data=request.model_dump())  # type: ignore
        return LoadModelsResponse(**data)

    def raise_error(self, request: dict):
        return self.get(endpoint="raise-error/", data=request)

import logging

from the_spymaster_solvers_api.structs.requests import LoadModelsRequest
from the_spymaster_solvers_api.structs.responses import LoadModelsResponse
from the_spymaster_util.http.client import DEFAULT_RETRY_STRATEGY, HTTPClient
from urllib3 import Retry

from .structs import (
    SERVICE_ERRORS,
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from .structs.classic.requests import ClassicStartGameRequest
from .structs.classic.responses import (
    ClassicClueResponse,
    ClassicGetGameStateResponse,
    ClassicGuessResponse,
    ClassicNextMoveResponse,
    ClassicStartGameResponse,
)
from .structs.duet.requests import DuetStartGameRequest
from .structs.duet.responses import (
    DuetClueResponse,
    DuetGetGameStateResponse,
    DuetGuessResponse,
    DuetNextMoveResponse,
    DuetStartGameResponse,
)

log = logging.getLogger(__name__)


class ClassicClient(HTTPClient):
    def __init__(self, game_api_url: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        super().__init__(
            base_url=f"{game_api_url}/classic",
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )

    def start_game(self, request: ClassicStartGameRequest) -> ClassicStartGameResponse:
        data = self.post(endpoint="start/", data=request.model_dump(), error_types={})
        return ClassicStartGameResponse(**data)

    def clue(self, request: ClueRequest) -> ClassicClueResponse:
        data = self.post(endpoint="clue/", data=request.model_dump())
        return ClassicClueResponse(**data)

    def guess(self, request: GuessRequest) -> ClassicGuessResponse:
        data = self.post(endpoint="guess/", data=request.model_dump())
        return ClassicGuessResponse(**data)

    def next_move(self, request: NextMoveRequest) -> ClassicNextMoveResponse:
        data = self.post(endpoint="next-move/", data=request.model_dump())
        return ClassicNextMoveResponse(**data)

    def get_game_state(self, request: GetGameStateRequest) -> ClassicGetGameStateResponse:
        data = self.get(endpoint="state/", data=request.model_dump())
        return ClassicGetGameStateResponse(**data)


class DuetClient(HTTPClient):
    def __init__(self, game_api_url: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        super().__init__(
            base_url=f"{game_api_url}/duet",
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )

    def start_game(self, request: DuetStartGameRequest) -> DuetStartGameResponse:
        data = self.post(endpoint="start/", data=request.model_dump(), error_types={})
        return DuetStartGameResponse(**data)

    def clue(self, request: ClueRequest) -> DuetClueResponse:
        data = self.post(endpoint="clue/", data=request.model_dump())
        return DuetClueResponse(**data)

    def guess(self, request: GuessRequest) -> DuetGuessResponse:
        data = self.post(endpoint="guess/", data=request.model_dump())
        return DuetGuessResponse(**data)

    def next_move(self, request: NextMoveRequest) -> DuetNextMoveResponse:
        data = self.post(endpoint="next-move/", data=request.model_dump())
        return DuetNextMoveResponse(**data)

    def get_game_state(self, request: GetGameStateRequest) -> DuetGetGameStateResponse:
        data = self.get(endpoint="state/", data=request.model_dump())
        return DuetGetGameStateResponse(**data)


class TheSpymasterClient(HTTPClient):
    def __init__(self, server_host: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        game_api_url = f"{server_host}/api/v1/game"
        super().__init__(
            base_url=game_api_url,
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )
        self.classic = ClassicClient(game_api_url=game_api_url, retry_strategy=retry_strategy)
        self.duet = DuetClient(game_api_url=game_api_url, retry_strategy=retry_strategy)

    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        data = self.post(endpoint="load-models/", data=request.model_dump())
        return LoadModelsResponse(**data)

    def raise_error(self, request: dict):
        return self.get(endpoint="raise-error/", data=request)

import logging

from the_spymaster_solvers_api.structs.requests import LoadModelsRequest
from the_spymaster_solvers_api.structs.responses import LoadModelsResponse
from the_spymaster_util.http.client import DEFAULT_RETRY_STRATEGY, HTTPClient
from urllib3 import Retry

from .client_classic import ClassicGameClient
from .client_duet import DuetGameClient
from .client_mini import MiniGameClient
from .structs import SERVICE_ERRORS

log = logging.getLogger(__name__)


class TheSpymasterClient(HTTPClient):
    def __init__(self, server_host: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        game_api_url = f"{server_host}/api/v1/game"
        super().__init__(
            base_url=game_api_url,
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )
        self.classic = ClassicGameClient(game_api_url=game_api_url, retry_strategy=retry_strategy)
        self.duet = DuetGameClient(game_api_url=game_api_url, retry_strategy=retry_strategy)
        self.mini = MiniGameClient(game_api_url=game_api_url, retry_strategy=retry_strategy)

    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        data = self.post(endpoint="load-models/", data=request.model_dump())
        return LoadModelsResponse(**data)

    def raise_error(self, request: dict):
        return self.get(endpoint="raise-error/", data=request)

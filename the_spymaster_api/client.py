import json
import logging
from typing import Callable

import requests
from requests import Response

from .structs import (
    GetGameStateRequest,
    GetGameStateResponse,
    GuessRequest,
    GuessResponse,
    HintRequest,
    HintResponse,
    LoadModelsRequest,
    LoadModelsResponse,
    NextMoveRequest,
    NextMoveResponse,
    StartGameRequest,
    StartGameResponse,
)

log = logging.getLogger(__name__)
DEFAULT_BASE_BACKEND = "http://localhost:8000"
CONTEXT_HEADER_KEY = "x-spymaster-context"
CONTEXT_ID_HEADER_KEY = "x-spymaster-context-id"


def _log_data(url: str, response: Response):
    try:
        data = response.json()
    except Exception:  # noqa
        data = response.content
    log.debug(
        f"Got status code {response.status_code}.",
        extra={"status_code": response.status_code, "url": url, "data": data},
    )


class TheSpymasterClient:
    def __init__(self, base_backend: str = None):
        if not base_backend:
            base_backend = DEFAULT_BASE_BACKEND
        self.base_url = f"{base_backend}/api/v1/game"
        log.debug(f"Client using backend: {self.base_url}.")

    def _http_call(self, endpoint: str, method: Callable, **kwargs) -> dict:
        url = f"{self.base_url}/{endpoint}"
        headers = kwargs.pop("headers", None) or {}
        log_context = getattr(log, "context", None)
        if log_context:
            headers[CONTEXT_HEADER_KEY] = json.dumps(log_context)
        response = method(url, headers=headers, **kwargs)
        _log_data(url=url, response=response)
        response.raise_for_status()
        data = response.json()
        return data

    def _get(self, endpoint: str, data: dict) -> dict:
        return self._http_call(endpoint=endpoint, method=requests.get, params=data)

    def _post(self, endpoint: str, data: dict) -> dict:
        return self._http_call(endpoint=endpoint, method=requests.post, json=data)

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

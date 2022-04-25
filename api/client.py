from typing import Callable

import requests
from requests import Response

from api.models.request import (
    GetGameStateRequest,
    GuessRequest,
    HintRequest,
    NextMoveRequest,
    StartGameRequest,
)
from api.models.response import (
    GetGameStateResponse,
    GuessResponse,
    HintResponse,
    NextMoveResponse,
    StartGameResponse,
)
from the_spymaster.utils import get_logger

log = get_logger(__name__)
DEFAULT_BASE_URL = "http://localhost:8000/api/v1/game"


def _log_data(url: str, response: Response):
    try:
        data = response.json()
    except Exception:
        data = response.content
    log.debug(
        f"Got status code {response.status_code}.",
        extra={"status_code": response.status_code, "url": url, "data": data},
    )


class TheSpymasterClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url

    def _http_call(self, endpoint: str, method: Callable, **kwargs) -> dict:
        url = f"{self.base_url}/{endpoint}"
        response = method(url, **kwargs)
        _log_data(url=url, response=response)
        response.raise_for_status()
        data = response.json()
        return data

    def _get(self, endpoint: str, data: dict) -> dict:
        return self._http_call(endpoint=endpoint, method=requests.get, params=data)

    def _post(self, endpoint: str, data: dict) -> dict:
        return self._http_call(endpoint=endpoint, method=requests.post, json=data)

    def start_game(self, request: StartGameRequest) -> StartGameResponse:
        return StartGameResponse(**self._post("start/", request.dict()))

    def hint(self, request: HintRequest) -> HintResponse:
        return HintResponse(**self._post("hint/", request.dict()))

    def guess(self, request: GuessRequest) -> GuessResponse:
        return GuessResponse(**self._post("guess/", request.dict()))

    def next_move(self, request: NextMoveRequest) -> NextMoveResponse:
        return NextMoveResponse(**self._post("next-move/", request.dict()))

    def get_game_state(self, request: GetGameStateRequest) -> GetGameStateResponse:
        return GetGameStateResponse(**self._get("state/", request.dict()))

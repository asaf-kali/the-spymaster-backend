import requests

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

DEFAULT_BASE_URL = "http://localhost:8000/api/v1/game"


class TheSpymasterClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url

    def _get(self, endpoint: str, data: dict) -> dict:
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, data=data)
        return response.json()

    def _post(self, endpoint: str, data: dict) -> dict:
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data)
        data = response.json()
        return data

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

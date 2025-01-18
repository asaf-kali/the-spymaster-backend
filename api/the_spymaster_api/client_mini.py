from the_spymaster_api.structs import (
    SERVICE_ERRORS,
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from the_spymaster_api.structs.mini.requests import MiniStartGameRequest
from the_spymaster_api.structs.mini.responses import (
    MiniClueResponse,
    MiniGetGameStateResponse,
    MiniGuessResponse,
    MiniNextMoveResponse,
    MiniStartGameResponse,
)
from the_spymaster_util.http.client import DEFAULT_RETRY_STRATEGY, HTTPClient
from urllib3 import Retry


class MiniGameClient(HTTPClient):
    def __init__(self, game_api_url: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        super().__init__(
            base_url=f"{game_api_url}/mini",
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )

    def start_game(self, request: MiniStartGameRequest) -> MiniStartGameResponse:
        data = self.post(endpoint="start/", data=request.model_dump())
        return MiniStartGameResponse(**data)

    def clue(self, request: ClueRequest) -> MiniClueResponse:
        data = self.post(endpoint="clue/", data=request.model_dump())
        return MiniClueResponse(**data)

    def guess(self, request: GuessRequest) -> MiniGuessResponse:
        data = self.post(endpoint="guess/", data=request.model_dump())
        return MiniGuessResponse(**data)

    def next_move(self, request: NextMoveRequest) -> MiniNextMoveResponse:
        data = self.post(endpoint="next-move/", data=request.model_dump())
        return MiniNextMoveResponse(**data)

    def get_game_state(self, request: GetGameStateRequest) -> MiniGetGameStateResponse:
        data = self.get(endpoint="state/", data=request.model_dump())
        return MiniGetGameStateResponse(**data)

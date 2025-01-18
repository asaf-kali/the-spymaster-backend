from the_spymaster_api.structs import (
    SERVICE_ERRORS,
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from the_spymaster_api.structs.classic.requests import ClassicStartGameRequest
from the_spymaster_api.structs.classic.responses import (
    ClassicClueResponse,
    ClassicGetGameStateResponse,
    ClassicGuessResponse,
    ClassicNextMoveResponse,
    ClassicStartGameResponse,
)
from the_spymaster_util.http.client import DEFAULT_RETRY_STRATEGY, HTTPClient
from urllib3 import Retry


class ClassicGameClient(HTTPClient):
    def __init__(self, game_api_url: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        super().__init__(
            base_url=f"{game_api_url}/classic",
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )

    def start_game(self, request: ClassicStartGameRequest) -> ClassicStartGameResponse:
        data = self.post(endpoint="start/", data=request.model_dump())
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

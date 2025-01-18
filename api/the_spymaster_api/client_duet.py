from the_spymaster_api.structs import (
    SERVICE_ERRORS,
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from the_spymaster_api.structs.duet.requests import DuetStartGameRequest
from the_spymaster_api.structs.duet.responses import (
    DuetClueResponse,
    DuetGetGameStateResponse,
    DuetGuessResponse,
    DuetNextMoveResponse,
    DuetStartGameResponse,
)
from the_spymaster_util.http.client import DEFAULT_RETRY_STRATEGY, HTTPClient
from urllib3 import Retry


class DuetGameClient(HTTPClient):
    def __init__(self, game_api_url: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        super().__init__(
            base_url=f"{game_api_url}/duet",
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )

    def start_game(self, request: DuetStartGameRequest) -> DuetStartGameResponse:
        data = self.post(endpoint="start/", data=request.model_dump())
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

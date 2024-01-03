import requests
import ulid
from codenames.boards.builder import generate_board
from codenames.game.move import Guess, Hint
from codenames.game.state import build_game_state
from rest_framework.viewsets import GenericViewSet
from the_spymaster_api.structs import (
    BaseRequest,
    GetGameStateRequest,
    GetGameStateResponse,
    GuessRequest,
    GuessResponse,
    HintRequest,
    HintResponse,
    HttpResponse,
    NextMoveRequest,
    NextMoveResponse,
    StartGameRequest,
    StartGameResponse,
)
from the_spymaster_solvers_api.structs.requests import LoadModelsRequest
from the_spymaster_solvers_api.structs.responses import LoadModelsResponse
from the_spymaster_util.http.errors import BadRequestError
from the_spymaster_util.logger import get_logger

from server.logic.db import load_game, save_game
from server.logic.next_move import NextMoveHandler
from server.logic.solvers import get_solvers_client
from server.models.game import Game
from server.views.endpoint import HttpMethod, endpoint

log = get_logger(__name__)


def ulid_lower():
    return ulid.new().str.lower()


class GameManagerView(GenericViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.solvers_client = get_solvers_client()

    @endpoint
    def start(self, request: StartGameRequest) -> StartGameResponse:
        board = generate_board(language=request.language, first_team=request.first_team)
        game_state = build_game_state(board=board)
        game = Game(id=ulid_lower(), state_data=game_state.dict())
        save_game(game)
        log.info(f"Starting game: {game.id}")
        return StartGameResponse(game_id=game.id, game_state=game_state)

    @endpoint
    def hint(self, request: HintRequest) -> HintResponse:
        game = load_game(request.game_id)
        game_state = game.state
        hint = Hint(word=request.word, card_amount=request.card_amount, for_words=request.for_words)
        given_hint = game_state.process_hint(hint)
        game.state_data = game_state.dict()
        save_game(game)
        return HintResponse(given_hint=given_hint, game_state=game_state)

    @endpoint
    def guess(self, request: GuessRequest) -> GuessResponse:
        game = load_game(request.game_id)
        game_state = game.state
        guess = Guess(card_index=request.card_index)
        given_guess = game_state.process_guess(guess)
        game.state_data = game_state.dict()
        save_game(game)
        return GuessResponse(given_guess=given_guess, game_state=game_state)

    @endpoint(methods=[HttpMethod.GET], url_path="state")
    def get_game_state(self, request: GetGameStateRequest) -> GetGameStateResponse:
        game = load_game(request.game_id)
        return GetGameStateResponse(game_state=game.state)

    @endpoint(url_path="next-move")
    def next_move(self, request: NextMoveRequest) -> NextMoveResponse:
        game = load_game(request.game_id)
        game_state = game.state
        handler = NextMoveHandler(
            game_state=game_state, solver=request.solver, model_identifier=request.model_identifier
        )
        response = handler.handle()
        game.state_data = handler.game_state.dict()
        save_game(game)
        return response

    @endpoint(url_path="load-models")
    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        response = self.solvers_client.load_models(request)
        return response

    @endpoint(methods=[HttpMethod.GET])
    def test(self, request: BaseRequest) -> HttpResponse:  # pylint: disable=unused-argument
        body = {"details": "It seems everything is working!"}
        return HttpResponse(body=body)

    @endpoint(methods=[HttpMethod.GET], url_path="raise-error")
    def raise_error(self, request: BaseRequest) -> HttpResponse:
        if getattr(request, "handled", False):
            raise BadRequestError(message="This error should be handled!")
        if getattr(request, "good", False):
            return HttpResponse(body={"success": "true"})
        raise Exception("Test error")  # pylint: disable=broad-exception-raised

    @endpoint(methods=[HttpMethod.GET], url_path="ping-google")
    def ping_google(self, request: BaseRequest) -> HttpResponse:  # pylint: disable=unused-argument
        response = requests.get("https://www.google.com", timeout=10)
        body = {"status_code": response.status_code, "duration": response.elapsed.total_seconds()}
        return HttpResponse(body=body)

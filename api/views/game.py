from codenames.game import Guess, Hint, build_game_state
from rest_framework.viewsets import GenericViewSet

from api.logic.game import NextMoveHandler, get_game
from api.logic.language import load_models
from api.models.game import Game
from api.structs.request import (
    BaseRequest,
    GetGameStateRequest,
    GuessRequest,
    HintRequest,
    LoadModelsRequest,
    NextMoveRequest,
    StartGameRequest,
)
from api.structs.response import (
    GetGameStateResponse,
    GuessResponse,
    HintResponse,
    LoadModelsResponse,
    NextMoveResponse,
    StartGameResponse,
)
from api.views import ViewContextMixin
from api.views.endpoint import HttpMethod, endpoint
from the_spymaster.utils import get_logger

log = get_logger(__name__)


class GameManagerView(GenericViewSet, ViewContextMixin):
    @endpoint
    def start(self, request: StartGameRequest) -> StartGameResponse:
        game_state = build_game_state(language=request.language)
        game = Game.objects.create(state_data=game_state.dict())
        return StartGameResponse(game_id=game.id, game_state=game_state)

    @endpoint
    def hint(self, request: HintRequest) -> HintResponse:
        game = get_game(request.game_id)
        game_state = game.state
        hint = Hint(word=request.word, card_amount=request.card_amount, for_words=request.for_words)
        given_hint = game_state.process_hint(hint)
        game.state_data = game_state.dict()
        game.save()
        return HintResponse(given_hint=given_hint, game_state=game_state)

    @endpoint
    def guess(self, request: GuessRequest) -> GuessResponse:
        game = get_game(request.game_id)
        game_state = game.state
        guess = Guess(card_index=request.card_index)
        given_guess = game_state.process_guess(guess)
        game.state_data = game_state.dict()
        game.save()
        return GuessResponse(given_guess=given_guess, game_state=game_state)

    @endpoint(methods=[HttpMethod.GET], url_path="state")
    def get_game_state(self, request: GetGameStateRequest) -> GetGameStateResponse:
        game = get_game(request.game_id)
        return GetGameStateResponse(game_state=game.state)

    @endpoint(url_path="next-move")
    def next_move(self, request: NextMoveRequest) -> NextMoveResponse:
        game = get_game(request.game_id)
        game_state = game.state
        handler = NextMoveHandler(
            game_state=game_state, solver=request.solver, model_identifier=request.model_identifier
        )
        response = handler.handle()
        game.state_data = handler.game_state.dict()
        game.save()
        return response

    @endpoint(url_path="load-models")
    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        loaded_models_count = load_models(model_ids=request.model_identifiers)
        return LoadModelsResponse(loaded_models_count=loaded_models_count)

    @endpoint(methods=[HttpMethod.GET])
    def test(self, request: BaseRequest) -> dict:
        return {"test": "test", "status_code": 200}

    @endpoint(methods=[HttpMethod.GET], url_path="raise-error")
    def raise_error(self, request: BaseRequest) -> dict:
        raise Exception("Test error")

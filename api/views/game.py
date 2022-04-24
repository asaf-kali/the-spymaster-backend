from codenames.game import Guess, Hint, build_game_state
from rest_framework.viewsets import GenericViewSet

from api.logic.errors import BadRequestError
from api.models.game import Game
from api.models.request import (
    GetGameStateRequest,
    GuessRequest,
    HintRequest,
    StartGameRequest,
)
from api.models.response import (
    GetGameStateResponse,
    GuessResponse,
    HintResponse,
    StartGameResponse,
)
from api.views import ViewContextMixin
from api.views.endpoint import endpoint
from the_spymaster.utils import get_logger

log = get_logger(__name__)


class GameManagerView(GenericViewSet, ViewContextMixin):
    @endpoint
    def start(self, request: StartGameRequest) -> StartGameResponse:
        game_state = build_game_state(language=request.language)
        game = Game.objects.create(state_json=game_state.json())
        return StartGameResponse(game_id=game.id, game_state=game_state)

    @endpoint
    def hint(self, request: HintRequest) -> HintResponse:
        game = _get_game(request.game_id)
        game_state = game.state
        hint = Hint(word=request.word, card_amount=request.card_amount)
        given_hint = game_state.process_hint(hint)
        game.state_json = game_state.json()
        game.save()
        return HintResponse(given_hint=given_hint, game_state=game_state)

    @endpoint
    def guess(self, request: GuessRequest) -> GuessResponse:
        game = _get_game(request.game_id)
        game_state = game.state
        guess = Guess(card_index=request.card_index)
        given_guess = game_state.process_guess(guess)
        game.state_json = game_state.json()
        game.save()
        return GuessResponse(given_guess=given_guess, game_state=game_state)

    @endpoint(methods=["GET"], url_path="get-state")
    def get_game_state(self, request: GetGameStateRequest) -> GetGameStateResponse:
        game = _get_game(request.game_id)
        return GetGameStateResponse(game_state=game.state)


def _get_game(game_id: int) -> Game:
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist as e:
        raise BadRequestError("Game does not exist") from e
    return game

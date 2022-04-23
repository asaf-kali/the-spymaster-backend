from codenames.game import Guess, Hint, build_game_state
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from api.logic.errors import BadRequestError
from api.models.game import Game
from api.views import ViewContextMixin


class GameManagerView(GenericViewSet, ViewContextMixin):
    @action(detail=False, methods=["post"])
    def start(self, request: Request) -> HttpResponse:
        language = request.data.get("language") or "english"
        game_state = build_game_state(language=language)
        game = Game.objects.create(state_json=game_state.json())
        data = {"game_id": game.id, "game_state": game_state.dict()}
        return JsonResponse(data=data)

    @action(detail=False, methods=["post"])
    def hint(self, request: Request) -> HttpResponse:
        try:
            game_id = int(request.data.get("game_id"))
            word = request.data.get("word")
            card_amount = int(request.data.get("card_amount"))
        except ValueError as e:
            raise BadRequestError("Failed parsing values") from e
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist as e:
            raise BadRequestError("Game does not exist") from e
        game_state = game.state
        hint = Hint(word=word, card_amount=card_amount)
        given_hint = game_state.process_hint(hint)
        game.state_json = game_state.json()
        game.save()
        data = {"given_hint": given_hint.dict(), "game_state": game_state.dict()}
        return JsonResponse(data=data)

    @action(detail=False, methods=["post"])
    def guess(self, request: Request) -> HttpResponse:
        try:
            game_id = int(request.data.get("game_id"))
            card_index = int(request.data.get("card_index"))
        except ValueError as e:
            raise BadRequestError("Failed parsing values") from e
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist as e:
            raise BadRequestError("Game does not exist") from e
        game_state = game.state
        guess = Guess(card_index=card_index)
        given_guess = game_state.process_guess(guess)
        game.state_json = game_state.json()
        game.save()
        data = {"given_guess": given_guess.dict(), "game_state": game_state.dict()}
        return JsonResponse(data=data)

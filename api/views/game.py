from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from api.logic.game import start_game_in_new_thread
from api.views import ViewContextMixin


class GameManagerView(GenericViewSet, ViewContextMixin):
    @action(detail=False, methods=["post"])
    def start(self, request: Request) -> HttpResponse:
        game_id = start_game_in_new_thread()
        data = {"game_id": game_id}
        return JsonResponse(data=data)

# pylint: disable=R0801

import requests
import ulid
from rest_framework.viewsets import GenericViewSet
from the_spymaster_api.structs import BaseRequest, HttpResponse
from the_spymaster_solvers_api.structs.requests import LoadModelsRequest
from the_spymaster_solvers_api.structs.responses import LoadModelsResponse
from the_spymaster_util.http.errors import BadRequestError
from the_spymaster_util.logger import get_logger

from server.logic.solvers import get_solvers_client
from server.views.endpoint import HttpMethod, endpoint

log = get_logger(__name__)


class GameView(GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.solvers_client = get_solvers_client()

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


def ulid_lower():
    return ulid.new().str.lower()

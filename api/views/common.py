import json

from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.viewsets import ViewSetMixin

from the_spymaster.utils import get_logger, wrap

log = get_logger(__name__)


class ViewContextMixin(ViewSetMixin):
    def initialize_request(self, request: WSGIRequest, *args, **kwargs) -> WSGIRequest:
        request = super().initialize_request(request, *args, **kwargs)
        try:
            user = request.user
        except AuthenticationFailed:
            user = AnonymousUser()
        request_context = _extract_context(request)
        log.set_context(context=request_context, django_user_id=user.id)
        log.debug(f"{wrap(request.method)} to {wrap(request.path)} by {wrap(user)}")
        return request


def _extract_context(request: WSGIRequest) -> dict:
    try:
        context_json = request.headers.get("x-context")
        return json.loads(context_json)
    except:  # noqa
        return {}

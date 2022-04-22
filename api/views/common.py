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
        log.update_context(user_id=user.id, method=request.method, path=request.path)
        log.debug(f"{wrap(request.method)} to {wrap(request.path)} by {wrap(user)}")
        return request

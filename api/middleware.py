import sentry_sdk
from codenames.game import GameRuleError
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from api.logic.errors import BadRequestError
from the_spymaster.utils import get_logger, wrap

log = get_logger(__name__)


class SpymasterExceptionHandlerMiddleware(MiddlewareMixin):
    def process_exception(self, request: WSGIRequest, exception: Exception):
        log.debug("Processing exception: %s", exception)
        if isinstance(exception, ValidationError):
            return JsonResponse({"message": str(exception)}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(exception, BadRequestError):
            return JsonResponse(
                {"message": exception.message, "details": exception.details}, status=exception.status_code
            )
        if isinstance(exception, PermissionDenied):
            log.warning(f"User {wrap(request.user)} can't access {wrap(request.path)}!")
            raise exception
        if isinstance(exception, GameRuleError):
            return JsonResponse(
                {"message": "Invalid move", "details": str(exception)}, status=status.HTTP_400_BAD_REQUEST
            )
        sentry_sdk.capture_exception(exception)
        log.exception("Uncaught exception")
        sentry_sdk.flush(timeout=5)
        if settings.DEBUG:
            return JsonResponse({"message": str(exception)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise exception

import sentry_sdk
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from api.logic.errors import BadRequestError, SpymasterError
from utils import get_logger, wrap

log = get_logger(__name__)


class SpymasterExceptionHandlerMiddleware(MiddlewareMixin):
    def process_exception(self, request: WSGIRequest, exception: Exception):
        log.error(exception)
        if isinstance(exception, ValidationError):
            return JsonResponse({"message": str(exception)}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(exception, BadRequestError):
            return JsonResponse({"message": exception.message}, status=exception.status)
        if isinstance(exception, PermissionDenied):
            log.warning(f"User {wrap(request.user)} can't access {wrap(request.path)}!")
            raise exception
        sentry_sdk.capture_exception(exception)
        if isinstance(exception, SpymasterError) and settings.DEBUG:
            return JsonResponse({"message": str(exception)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise exception

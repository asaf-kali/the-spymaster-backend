import json

import sentry_sdk
from codenames.game import GameRuleError
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.http.response import HttpResponseBase
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from the_spymaster_util import get_logger, wrap
from the_spymaster_util.http_client import CONTEXT_HEADER_KEY, CONTEXT_ID_HEADER_KEY
from the_spymaster_util.measure_time import MeasureTime

from api.logic.errors import BadRequestError

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
        message = "Internal server error" if not settings.DEBUG else str(exception)
        data = {"message": message, "context_id": log.context_id}
        headers = {CONTEXT_ID_HEADER_KEY: log.context_id}
        return JsonResponse(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR, headers=headers)


class ContextLoggingMiddleware(MiddlewareMixin):
    def __call__(self, request: WSGIRequest):
        _log_request(request)
        with MeasureTime() as mt:
            response = super().__call__(request)
        _log_response(response, duration=mt.delta)
        return response

    async def __acall__(self, request: WSGIRequest):
        _log_request(request)
        with MeasureTime() as mt:
            response = await super().__acall__(request)
        _log_response(response, duration=mt.delta)
        return response


def _log_request(request: WSGIRequest):
    try:
        user = request.user
    except AuthenticationFailed:
        user = AnonymousUser()
    request_context = _extract_context(request)
    log.set_context(context=request_context, django_user_id=user.id)
    try:
        data = json.loads(request.body.decode())
    except:  # noqa
        data = {}
    log.debug(f"{wrap(request.method)} to {wrap(request.path)} by {wrap(user)}", extra={"data": data})
    return request


def _log_response(response: HttpResponseBase, duration: float):
    status_code = getattr(response, "status_code", None)
    log.info(f"Returning status {wrap(status_code)}", extra={"duration": duration})
    log.reset_context()
    return response


def _extract_context(request: WSGIRequest) -> dict:
    try:
        context_json = request.headers.get(CONTEXT_HEADER_KEY)
        if not context_json:
            return {}
        return json.loads(context_json)
    except Exception as e:
        log.debug(f"Failed to extract context from request: {e}")
        return {}

import json
import traceback

import sentry_sdk
from codenames.game import GameRuleError
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.http.response import HttpResponseBase
from django.utils.deprecation import MiddlewareMixin
from requests import HTTPError
from rest_framework import status
from the_spymaster_util.http_client import (
    CONTEXT_ID_HEADER_KEY,
    extract_context,
    get_error_code,
)
from the_spymaster_util.logger import get_logger, wrap
from the_spymaster_util.measure_time import MeasureTime

from api.structs.errors import BadRequestError

log = get_logger(__name__)


class SpymasterExceptionHandlerMiddleware(MiddlewareMixin):
    def process_exception(self, request: WSGIRequest, exception: Exception):
        log.debug("Processing exception: %s", exception, exc_info=True)
        error_code = get_error_code(exception)
        if isinstance(exception, ValidationError):
            return JsonResponse(
                {"message": str(exception), "error_code": error_code}, status=status.HTTP_400_BAD_REQUEST
            )
        if isinstance(exception, BadRequestError):
            return JsonResponse(
                {"message": exception.message, "error_code": error_code, "details": exception.details},
                status=exception.status_code,
            )
        if isinstance(exception, PermissionDenied):
            log.warning(f"User {wrap(request.user)} can't access {wrap(request.path)}!")
            raise exception
        if isinstance(exception, GameRuleError):
            return JsonResponse(
                {"message": "Invalid move", "error_code": error_code, "details": str(exception)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if isinstance(exception, HTTPError) and exception.response is not None:
            response = exception.response
            try:
                data = response.json()
            except:  # noqa
                data = {"message": "Internal server error", "error_code": error_code, "details": response.text}
            return JsonResponse(data=data, status=response.status_code)

        sentry_sdk.capture_exception(exception)
        log.exception("Uncaught exception")
        sentry_sdk.flush(timeout=5)
        message = "Internal server error" if not settings.DEBUG else str(exception)
        data = {"message": message, "error_code": error_code, "context_id": log.context_id}
        if settings.DEBUG:
            data["details"] = traceback.format_exc()
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
    request_context = extract_context(request.headers)
    log.set_context(context=request_context)
    try:
        data = json.loads(request.body.decode())
    except:  # noqa
        data = {}
    log.debug(f"Handling: {wrap(request.method)} to {wrap(request.path)}", extra={"data": data})
    return request


def _log_response(response: HttpResponseBase, duration: float):
    status_code = getattr(response, "status_code", None)
    log.info(f"Responding: {wrap(status_code)}", extra={"duration": duration})
    log.reset_context()
    return response

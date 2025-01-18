import json
import traceback
from typing import Any, Mapping

import sentry_sdk
from codenames.generic.exceptions import GameRuleError
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.http.response import HttpResponseBase
from django.utils.deprecation import MiddlewareMixin
from the_spymaster_api.structs import APIGameRuleError
from the_spymaster_util.http.client import extract_context
from the_spymaster_util.http.defs import CONTEXT_ID_HEADER_KEY
from the_spymaster_util.http.errors import (
    APIError,
    BadRequestError,
    ForbiddenError,
    InternalServerError,
)
from the_spymaster_util.logger import get_logger, wrap
from the_spymaster_util.measure_time import MeasureTime

log = get_logger(__name__)


def response_from_api_error(
    e: APIError, override_error_code: str | None = None  # pylint: disable=invalid-name
) -> HttpResponseBase:
    data = e.response_payload
    if override_error_code:
        data["error_code"] = override_error_code
    headers = {CONTEXT_ID_HEADER_KEY: log.context_id}
    return JsonResponse(data=data, status=e.status_code, headers=headers)


class SpymasterExceptionHandlerMiddleware(MiddlewareMixin):
    def process_exception(self, request: WSGIRequest, exception: Exception):
        log.debug("Processing exception: %s", exception, exc_info=True)
        if isinstance(exception, BadRequestError):
            return response_from_api_error(e=exception)
        if isinstance(exception, ValidationError):
            api_error = BadRequestError(message=str(exception))
            return response_from_api_error(e=api_error)
        if isinstance(exception, PermissionDenied):
            log.info(f"User {wrap(request.user)} can't access {wrap(request.path)}!")
            api_error = ForbiddenError(message=str(exception))
            return response_from_api_error(e=api_error)
        if isinstance(exception, GameRuleError):
            api_error = APIGameRuleError.from_game_rule_error(exception)
            return response_from_api_error(e=api_error)
        # if isinstance(exception, HTTPError) and exception.response is not None:
        #     response = exception.response
        #     try:
        #         return JsonResponse(data=response.json(), status=response.status_code)
        #     except:  # noqa
        #         pass
        sentry_sdk.capture_exception(exception)
        log.exception("Uncaught exception")
        sentry_sdk.flush(timeout=5)
        if settings.DEBUG:
            data = {"exception_type": exception.__class__.__name__, "details": traceback.format_exc()}
            internal_error = InternalServerError(message=str(exception), data=data)
        else:
            internal_error = InternalServerError()
        return response_from_api_error(e=internal_error)


class ContextLoggingMiddleware(MiddlewareMixin):
    def __call__(self, request: WSGIRequest):
        _log_request(request)
        with MeasureTime() as mt:  # pylint: disable=invalid-name
            response = super().__call__(request)
        _log_response(response, duration=mt.delta)
        return response

    async def __acall__(self, request: WSGIRequest):
        _log_request(request)
        with MeasureTime() as mt:  # pylint: disable=invalid-name
            response = await super().__acall__(request)
        _log_response(response, duration=mt.delta)
        return response


def _log_request(request: WSGIRequest):
    request_context = extract_context(request.headers)
    log.set_context(context=request_context)
    try:
        data = json.loads(request.body.decode())
    except:  # noqa  # pylint: disable=invalid-name, bare-except
        data = {}
    data["request_meta"] = _get_string_values(request.META)  # Meta also contains headers
    log.debug(f"Handling: {wrap(request.method)} to {wrap(request.path)}", extra={"data": data})
    return request


def _log_response(response: HttpResponseBase, duration: float):
    status_code = getattr(response, "status_code", None)
    log.info(f"Responding: {wrap(status_code)}", extra={"duration": duration})
    log.reset_context()
    return response


def _get_string_values(m: Mapping[str, Any]) -> Mapping[str, str]:  # pylint: disable=invalid-name
    return {k.lower(): v for k, v in m.items() if isinstance(v, str)}

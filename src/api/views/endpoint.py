import functools
import json
from enum import Enum
from typing import List, Tuple, Type

from django.http import HttpResponse, JsonResponse
from pydantic import BaseModel, ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from the_spymaster_util.http_client import CONTEXT_ID_HEADER_KEY
from the_spymaster_util.logging import get_logger

from api.logic.errors import BadRequestError, SpymasterError
from api.structs import BaseRequest, BaseResponse

log = get_logger(__name__)

ALLOWED_REQUEST_TYPES = (BaseModel, BaseRequest)
ALLOWED_RESPONSE_TYPES = (dict, BaseModel, BaseResponse, HttpResponse)


class EndpointConfigurationError(SpymasterError):
    pass


class EndpointAnnotationError(EndpointConfigurationError):
    pass


class EndpointTypingError(EndpointConfigurationError):
    def __init__(self, message: str, actual_type: Type, supported_types: Tuple[Type]):
        detailed_message = f"{message} (actual type: {actual_type}, supported types: {supported_types})"
        super().__init__(detailed_message)
        self.actual_type = actual_type
        self.supported_types = supported_types


class ResponseStructureError(EndpointConfigurationError):
    pass


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


def endpoint(
    func=None, *, detail: bool = False, methods: List[HttpMethod] = None, url_path: str = None, url_name: str = None
):
    methods = methods or [HttpMethod.POST]
    str_methods = [m.value for m in methods]

    def decorator(f):
        endpoint_name = f.__name__
        request_model, response_model = _get_request_response_models(f)
        log.debug(f"Registering endpoint {endpoint_name}")

        @functools.wraps(f)
        def wrapper(view, request: Request, *args, **kwargs):
            log.update_context(endpoint_name=endpoint_name, django_user_id=request.user.id)
            parsed_request = _parse_request(request_model=request_model, drf_request=request)
            response = f(view, parsed_request)
            response_data = _get_response_data(response)
            status_code = response_data.pop("status_code", None)
            if not status_code:
                raise ResponseStructureError("Response data is missing status_code key!")
            headers = {CONTEXT_ID_HEADER_KEY: log.context_id}
            response = JsonResponse(data=response_data, status=status_code, headers=headers)
            if getattr(parsed_request, "debug", False):
                log.info("Response data", extra={"response": response_data})
            return response

        return action(detail=detail, methods=str_methods, url_path=url_path, url_name=url_name)(wrapper)

    if func:
        return decorator(func)
    return decorator


def _get_request_response_models(func) -> Tuple[Type[BaseRequest], Type]:
    func_name, annotations = func.__name__, func.__annotations__
    try:
        request_model = annotations["request"]
    except KeyError as e:
        raise EndpointAnnotationError(f"{func_name} is missing request type annotation!") from e
    try:
        response_model = annotations["return"]
    except KeyError as e:
        raise EndpointAnnotationError(f"{func_name} is missing return type annotation!") from e
    if not issubclass(request_model, ALLOWED_REQUEST_TYPES):
        raise EndpointTypingError(
            f"{func_name}'s request type annotation is not supported!",
            actual_type=request_model,
            supported_types=ALLOWED_REQUEST_TYPES,  # type: ignore
        )
    if not issubclass(response_model, ALLOWED_RESPONSE_TYPES):
        raise EndpointTypingError(
            f"{func_name}'s return type annotation is not supported!",
            actual_type=response_model,
            supported_types=ALLOWED_RESPONSE_TYPES,  # type: ignore
        )
    # if len(annotations) > 2:
    #     raise EndpointConfigurationError(f"{func_name} has more than 2 annotations!")
    return request_model, response_model


def _parse_request(request_model: Type[BaseModel], drf_request: Request) -> BaseModel:
    query_params = {k: v for k, v in drf_request.query_params.items()}
    data = {**query_params, **drf_request.data}
    try:
        parsed_request = request_model(drf_request=drf_request, **data)
    except Exception as e:
        details = e.errors() if isinstance(e, ValidationError) else str(e)
        raise BadRequestError("Request parsing failed.", details=details) from e  # type: ignore
    return parsed_request


def _get_response_data(response: BaseResponse) -> dict:
    if response is None:
        return {"status_code": status.HTTP_204_NO_CONTENT, "message": "No content"}
    if isinstance(response, BaseModel):
        return response.dict()
    if isinstance(response, HttpResponse):
        response_body = response.content.decode("utf-8")
        response_data = json.loads(response_body)
        return {**response_data, "status_code": response.status_code}
    if isinstance(response, dict):
        return response
    raise EndpointTypingError(
        "Response type not implemented",
        actual_type=type(response),
        supported_types=ALLOWED_RESPONSE_TYPES,  # type: ignore
    )

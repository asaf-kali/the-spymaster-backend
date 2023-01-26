import functools
import json
from enum import Enum
from typing import List, Optional, Tuple, Type, Union

from django.http import HttpResponse as DjangoHttpResponse
from django.http import JsonResponse
from pydantic import BaseModel, ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from the_spymaster_util.http_client import CONTEXT_ID_HEADER_KEY
from the_spymaster_util.logger import get_logger

from api.structs import BaseRequest, HttpResponse
from api.structs.errors import BadRequestError, SpymasterError

log = get_logger(__name__)

RequestType = Union[BaseModel, BaseRequest]
ResponseType = Union[dict, BaseModel, HttpResponse, DjangoHttpResponse]
ALLOWED_REQUEST_TYPES = RequestType.__args__  # type: ignore
ALLOWED_RESPONSE_TYPES = ResponseType.__args__  # type: ignore


class EndpointConfigurationError(SpymasterError):
    pass


class EndpointAnnotationError(EndpointConfigurationError):
    pass


class EndpointTypingError(EndpointConfigurationError):
    def __init__(self, message: str, actual_type: Type, supported_types: Tuple[Type, ...]):
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
    func=None,
    *,
    detail: bool = False,
    methods: Optional[List[HttpMethod]] = None,
    url_path: Optional[str] = None,
    url_name: Optional[str] = None,
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
            json_response = _get_json_response(response=response)
            if getattr(parsed_request, "debug", False):
                log.info("Response data", extra={"content": json_response.content})
            return json_response

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
    query_params = dict(drf_request.query_params.items())
    data = {**query_params, **drf_request.data}
    try:
        parsed_request = request_model(drf_request=drf_request, **data)
    except Exception as e:
        details = e.errors() if isinstance(e, ValidationError) else str(e)
        raise BadRequestError("Request parsing failed.", details=details) from e
    return parsed_request


def _get_json_response(response: ResponseType) -> JsonResponse:
    headers = {CONTEXT_ID_HEADER_KEY: log.context_id}
    status_code = status.HTTP_200_OK
    if response is None:
        data = {"message": "No content"}
    elif isinstance(response, dict):
        data = response
    elif isinstance(response, HttpResponse):
        status_code = response.status_code
        data = response.data
        if response.headers:
            headers.update(response.headers)
    elif isinstance(response, BaseModel):
        data = response.dict()
    elif isinstance(response, DjangoHttpResponse):
        status_code = response.status_code
        response_body = response.content.decode("utf-8")
        data = json.loads(response_body)
        headers.update(response.headers)
    else:
        raise EndpointTypingError(
            "Response type not implemented",
            actual_type=type(response),
            supported_types=ALLOWED_RESPONSE_TYPES,
        )
    return JsonResponse(data=data, status=status_code, headers=headers)

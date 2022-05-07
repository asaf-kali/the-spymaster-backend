import functools
from enum import Enum
from typing import List, Tuple, Type

from django.http import JsonResponse
from pydantic import BaseModel, ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request

from api.logic.errors import BadRequestError, SpymasterError
from api.models.response import BaseResponse
from the_spymaster.utils import get_logger

log = get_logger(__name__)


class EndpointConfigurationError(SpymasterError):
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
            log.update_context(endpoint_name=endpoint_name)
            log.info(f"Endpoint called: {endpoint_name}", extra={"request": request.data})
            parsed_request = _parse_request(request_model=request_model, drf_request=request)
            response = f(view, parsed_request)
            response_data = _get_response_data(response)
            status_code = response_data.pop("status_code")
            response = JsonResponse(response_data, status=status_code)
            log.reset_context()
            return response

        return action(detail=detail, methods=str_methods, url_path=url_path, url_name=url_name)(wrapper)

    if func:
        return decorator(func)
    return decorator


def _get_request_response_models(func) -> Tuple[Type[BaseModel], Type[BaseModel]]:
    func_name, annotations = func.__name__, func.__annotations__
    try:
        request_model = annotations["request"]
    except KeyError as e:
        raise EndpointConfigurationError(f"{func_name} is missing request type annotation!") from e
    try:
        response_model = annotations["return"]
    except KeyError as e:
        raise Exception(f"{func_name} is missing return type annotation!") from e
    if not issubclass(request_model, BaseModel):
        raise EndpointConfigurationError(f"{func_name}'s request type annotation is not a subclass of BaseModel!")
    if not issubclass(response_model, BaseModel):
        raise EndpointConfigurationError(f"{func_name}'s return type annotation is not a subclass of BaseModel!")
    if len(annotations) != 2:
        raise EndpointConfigurationError(f"{func_name} has more than 2 annotations!")
    return request_model, response_model


def _parse_request(request_model: Type[BaseModel], drf_request: Request) -> BaseModel:
    query_params = {k: v for k, v in drf_request.query_params.items()}
    data = {**query_params, **drf_request.data}
    try:
        parsed_request = request_model(drf_request=drf_request, **data)
    except Exception as e:
        details = e.errors() if isinstance(e, ValidationError) else str(e)
        raise BadRequestError("Request parsing failed.", details=details) from e
    return parsed_request


def _get_response_data(response: BaseResponse) -> dict:
    if response is None:
        return {"status_code": status.HTTP_204_NO_CONTENT, "message": "No content"}
    return response.dict()

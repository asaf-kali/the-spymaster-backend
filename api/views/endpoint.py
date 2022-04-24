import functools
from typing import Tuple, Type

from django.http import JsonResponse
from pydantic import BaseModel, ValidationError
from rest_framework.decorators import action
from rest_framework.request import Request

from api.logic.errors import BadRequestError
from api.views import log


class EndpointConfigurationError(Exception):
    pass


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


def endpoint(func):
    endpoint_name = func.__name__
    request_model, response_model = _get_request_response_models(func)

    @functools.wraps(func)
    def wrapper(view, request: Request, *args, **kwargs):
        log.set_context(dict(endpoint_name=endpoint_name))
        log.info(f"Endpoint called: {endpoint_name}", extra={"request": request.data})
        parsed_request = _parse_request(request_model=request_model, drf_request=request)
        response = func(view, parsed_request)
        response_data = response.dict()
        status_code = response_data.pop("status_code")
        return JsonResponse(response_data, status=status_code)

    return action(detail=False, methods=["post"])(wrapper)


def _parse_request(request_model: Type[BaseModel], drf_request: Request) -> BaseModel:
    try:
        parsed_request = request_model(drf_request=drf_request, **drf_request.data)
    except Exception as e:
        details = e.errors() if isinstance(e, ValidationError) else str(e)
        raise BadRequestError("Request parsing failed.", details=details) from e
    return parsed_request

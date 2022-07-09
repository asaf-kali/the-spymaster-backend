from typing import Optional

from rest_framework import status
from the_spymaster_util import JsonType, get_logger

log = get_logger(__name__)


class SpymasterError(Exception):
    pass


class ApiError(SpymasterError):
    def __init__(
        self,
        message: str = "Internal server error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[JsonType] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class BadRequestError(ApiError):
    def __init__(
        self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Optional[JsonType] = None
    ):
        super().__init__(message=message, status_code=status_code, details=details)

    @staticmethod
    def from_key_error(e: KeyError) -> "BadRequestError":
        return BadRequestError(f"Missing argument {e}")


class UnauthorizedError(BadRequestError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(BadRequestError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(BadRequestError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)

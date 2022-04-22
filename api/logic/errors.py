from rest_framework import status

from the_spymaster.utils import get_logger, wrap

log = get_logger(__name__)


class SpymasterError(Exception):
    pass


class EnvironmentSafetyError(SpymasterError):
    operation_name: str
    environment: str

    def __init__(self, operation_name: str, environment: str):
        self.operation_name = operation_name
        self.environment = environment
        super().__init__(f"Can't perform {wrap(self.operation_name)} on {wrap(self.environment)} environment")


class ConfigurationError(SpymasterError):
    pass


class BadRequestError(SpymasterError):
    status = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class MissingArgumentError(BadRequestError):
    arg_name: str

    def __init__(self, arg_name: str):
        self.arg_name = arg_name
        super().__init__(f"Missing argument {arg_name}")

    @staticmethod
    def from_key_error(e: KeyError) -> "MissingArgumentError":
        return MissingArgumentError(str(e))


class UnauthorizedError(BadRequestError):
    status = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(BadRequestError):
    status = status.HTTP_403_FORBIDDEN


class NotFoundError(BadRequestError):
    status = status.HTTP_404_NOT_FOUND

from typing import Tuple

from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request
from the_spymaster_util.http.errors import BadRequestError

from server.logic.recaptcha.validator import verify_recaptcha


class RecaptchaAuthentication(BaseAuthentication):
    def authenticate(self, request: Request) -> Tuple[AnonymousUser, str]:
        try:
            token = request.GET["recaptcha_token"]
        except KeyError as e:  # pylint: disable=invalid-name
            raise BadRequestError(message=f"Missing key {e}") from e
        verify_recaptcha(token=token)
        return AnonymousUser(), token

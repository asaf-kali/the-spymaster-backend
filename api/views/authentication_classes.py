from typing import Tuple

from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from api.logic.errors import MissingArgumentError
from api.logic.recaptcha.validator import verify_recaptcha


class RecaptchaAuthentication(BaseAuthentication):
    def authenticate(self, request: Request) -> Tuple[AnonymousUser, str]:
        try:
            token = request.GET["recaptcha_token"]
        except KeyError as e:
            raise MissingArgumentError.from_key_error(e)
        verify_recaptcha(token=token)
        return AnonymousUser(), token

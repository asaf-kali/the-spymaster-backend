import logging

import requests
from django.conf import settings
from prodict import Prodict

from api.logic.errors import ForbiddenError

log = logging.getLogger(__name__)


class RecaptchaVerification(Prodict):
    success: bool
    challenge_ts: str
    hostname: str
    error_codes: list


RECAPTCHA_FAILED_ERROR = ForbiddenError("reCAPTCHA Validation failed")


def verify_recaptcha(token: str, should_raise: bool = True) -> RecaptchaVerification:
    log.debug(f"Validating token: {token}")
    params = {"secret": settings.RECAPTCHA_PRIVATE_KEY, "response": token}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", params=params)
    data = response.json()
    log.debug(f"Validate response: {data}")
    verification = RecaptchaVerification.from_dict(data)
    if not verification.success and should_raise:
        raise RECAPTCHA_FAILED_ERROR
    return verification

import logging

import requests
from django.conf import settings
from pydantic import BaseModel
from the_spymaster_util.http.errors import ForbiddenError

log = logging.getLogger(__name__)


class RecaptchaVerification(BaseModel):
    success: bool | None = False
    challenge_ts: str | None = None
    hostname: str | None = None
    error_codes: list | None = None


RECAPTCHA_FAILED_ERROR = ForbiddenError(message="reCAPTCHA Validation failed")


def verify_recaptcha(token: str, should_raise: bool = True) -> RecaptchaVerification:
    log.debug(f"Validating token: {token}")
    params = {"secret": settings.RECAPTCHA_PRIVATE_KEY, "response": token}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", params=params, timeout=10)
    data = response.json()
    log.debug(f"Validate response: {data}")
    verification = RecaptchaVerification(**data)
    if not verification.success and should_raise:
        raise RECAPTCHA_FAILED_ERROR
    return verification

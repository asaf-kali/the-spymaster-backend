import logging
from typing import Optional

import requests
from django.conf import settings
from pydantic import BaseModel

from api.structs.errors import ForbiddenError

log = logging.getLogger(__name__)


class RecaptchaVerification(BaseModel):
    success: Optional[bool] = False
    challenge_ts: Optional[str] = None
    hostname: Optional[str] = None
    error_codes: Optional[list] = None


RECAPTCHA_FAILED_ERROR = ForbiddenError("reCAPTCHA Validation failed")


def verify_recaptcha(token: str, should_raise: bool = True) -> RecaptchaVerification:
    log.debug(f"Validating token: {token}")
    params = {"secret": settings.RECAPTCHA_PRIVATE_KEY, "response": token}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", params=params)
    data = response.json()
    log.debug(f"Validate response: {data}")
    verification = RecaptchaVerification(**data)
    if not verification.success and should_raise:
        raise RECAPTCHA_FAILED_ERROR
    return verification

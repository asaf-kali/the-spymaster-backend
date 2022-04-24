from typing import Optional

from pydantic import BaseModel
from rest_framework.request import Request

from api.models import SpymasterUser


class BaseRequest(BaseModel):
    drf_request: Request

    class Config:
        fields = {"drf_request": {"exclude": True}}
        arbitrary_types_allowed = True

    @property
    def preforming_user(self) -> SpymasterUser:
        return self.drf_request.user


class TestRequest(BaseRequest):
    game_id: int
    message: Optional[str] = None

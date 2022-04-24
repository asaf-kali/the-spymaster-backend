from pydantic import BaseModel


class BaseResponse(BaseModel):
    status_code: int = 200


class TestResponse(BaseResponse):
    message: str

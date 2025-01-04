from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict


class HttpResponse(BaseModel):
    status_code: int = 200
    headers: Optional[dict] = None
    body: Union[dict, BaseModel]

    @property
    def data(self) -> dict:
        if isinstance(self.body, BaseModel):
            return self.body.model_dump()
        return self.body


class ErrorResponse(BaseModel):
    message: Optional[str]
    details: Any
    model_config = ConfigDict(extra="allow")

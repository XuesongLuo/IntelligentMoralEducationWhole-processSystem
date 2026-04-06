from typing import Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any | None = None
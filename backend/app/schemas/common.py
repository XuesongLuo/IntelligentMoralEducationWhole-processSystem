from typing import Any
from pydantic import BaseModel, Field


class ResponseModel(BaseModel):
    code: int = Field(default=200, description="业务状态码")
    message: str = Field(default="success", description="响应消息")
    data: Any | None = Field(default=None, description="响应数据")
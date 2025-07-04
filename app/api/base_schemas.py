from typing import Any

from fastapi import status as status_code
from pydantic import BaseModel, ConfigDict, Field


class BaseError(BaseModel):
    type: str | None = Field(None, title="The name of the class of the error")
    title: str | None = Field(
        None,
        title="A short, human-readable summary of the problem that does not change from occurence to occurence",
    )
    detail: str | None = Field(None, title="А human-readable explanation specific to this occurrence of the problem")
    instance: Any | None = Field(None, title="Identifier for this specific occurrence of the problem")


class BaseResponse(BaseModel):
    status: int = Field(..., title="Status code of request.", examples=[status_code.HTTP_200_OK])
    error: dict[Any, Any] | BaseError | None = Field(None, title="Errors")
    payload: Any | None = Field({}, title="Payload data.")

    model_config = ConfigDict(json_schema_extra={})

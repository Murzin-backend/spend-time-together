from typing import Any, Generic, TypeAlias, TypeVar

from fastapi import (
    Response,
    status as http_status_code,
)
from pydantic import BaseModel, ConfigDict, Field

from app.api.base_schemas import BaseError

_Model = TypeVar("_Model")

GenericResponse: TypeAlias = BaseModel


class DataResponse(GenericResponse, Generic[_Model]):
    data: _Model


class OkResponse(GenericResponse, Generic[_Model]):
    status: int = Field(..., title="Status code of request.", examples=[http_status_code.HTTP_200_OK])
    error: dict[Any, Any] | BaseError | None = Field(None, title="Errors")
    payload: DataResponse[_Model] = Field(title="Payload data.")

    @classmethod
    def new(
        cls,
        *,
        status_code: int,
        model: type[_Model] | list[type[_Model]] | Any,
        data: _Model | Any,
    ) -> "OkResponse[_Model]":
        return cls[model](status=status_code, payload=DataResponse[model](data=data))  # type: ignore

    model_config = ConfigDict(json_schema_extra={"description": ""})

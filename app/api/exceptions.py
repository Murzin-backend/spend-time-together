from collections import defaultdict
from itertools import groupby
from typing import Any, Union

from fastapi import status
from fastapi.requests import Request
from starlette.responses import JSONResponse

from app.api.base_schemas import BaseResponse


class BaseAPIException(Exception):
    _content_type: str = "application/json"
    model: type[BaseResponse] = BaseResponse
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    title: str | None = None
    type: str | None = None
    detail: str | None = None
    instance: str | None = None
    headers: dict[str, str] | None = None

    def __init__(self, **ctx: Any) -> None:
        self.__dict__ = ctx

    def get_response_data(self) -> BaseResponse:
        return self.model(  # type: ignore[call-arg]
            status=self.status_code,
            error=self.model.model_fields["error"].annotation(
                type=self._get_type_error(),
                detail=self.detail,
                title=self.title,
                instance=self.instance,
            ),
        )

    def _get_type_error(self) -> str:
        return self.model.model_fields["error"].annotation.__name__

    @classmethod
    def example(cls) -> dict[str, Any] | None:
        if isinstance(cls.model.model_config.get("json_schema_extra"), dict):
            return cls.model.model_config["json_schema_extra"].get("example")
        return None

    @classmethod
    def response(cls) -> dict[str, Any]:
        return {
            "model": cls.model,
            "content": {
                cls._content_type: cls.model.model_config.get("json_schema_extra"),
            },
        }

def include_exception_responses(*args: type[BaseAPIException]) -> dict[Any, Any]:
    responses: dict[int, dict[Any, Any]] = {}

    for status_code, errs_iter in groupby(args, lambda e: e.status_code):
        errs = list(errs_iter)
        status_code = errs[0].status_code  # noqa: PLW2901
        if len(errs) == 1:
            responses.update({status_code: errs[0].response()})
        else:
            content: dict[Any, Any] = defaultdict(lambda: defaultdict(dict))
            for err in errs:
                content[err._content_type]["examples"].update({err.__name__: {"value": err.example()}})
            responses.update(
                {
                    status_code: {
                        "model": Union[tuple(err.model for err in errs)],
                        "content": dict(content),
                    }
                }
            )

    return responses


async def api_exception_handler(_: Request, exc: BaseAPIException) -> JSONResponse:
    """
    Обработчик для кастомных исключений API.
    Преобразует BaseAPIException в JSONResponse.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.get_response_data().model_dump(exclude_none=True),
        headers=exc.headers,
    )
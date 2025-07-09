from collections.abc import Iterable
from http import HTTPStatus
from typing import Any

from app.api.base_schemas import BaseResponse
from app.api.constants import HeaderDescription
from app.api.exceptions import BaseAPIException, include_exception_responses
from app.api.response_patterns import GenericResponse


def build_responses(
    *,
    status_code: int,
    docs_response_model: type[BaseResponse | GenericResponse] | None,
    exceptions: Iterable[type[BaseAPIException]] | None = None,
    additional_responses: dict[int, dict[str, str]] | None = None,
    additional_headers: dict[HTTPStatus, dict[str, HeaderDescription]] | None = None,
) -> dict[Any, Any]:
    responses: dict[Any, Any] = {status_code: {"model": docs_response_model}}

    if additional_responses:
        responses.update(additional_responses)
    if exceptions:
        responses.update(include_exception_responses(*exceptions))
    if additional_headers:
        for status, headers in additional_headers.items():
            if status in responses:
                current_headers = responses[status].get("headers", {})
                responses[status]["headers"] = {**current_headers, **headers}
    return responses
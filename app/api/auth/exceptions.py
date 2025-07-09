from fastapi import status
from pydantic import Field

from app.api.base_schemas import BaseError, BaseResponse

__all__ = (
    "UserNotFoundException",
    "UserAlreadyExistsException"
)

from app.api.exceptions import BaseAPIException


class UserNotFoundError(BaseError):
    pass


class UserNotFoundResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_401_UNAUTHORIZED])
    error: UserNotFoundError


class UserNotFoundException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    model = UserNotFoundResponseModel


class UserAlreadyExistsError(BaseError):
    pass


class UserAlreadyExistsResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_409_CONFLICT])
    error: UserAlreadyExistsError


class UserAlreadyExistsException(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    model = UserAlreadyExistsResponseModel
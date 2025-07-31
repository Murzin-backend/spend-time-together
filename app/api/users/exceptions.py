from fastapi import status
from pydantic import Field

from app.api.base_schemas import BaseError, BaseResponse

__all__ = (
    "UserNotFoundException",
    "UserConflictException",
    "UserBadRequestException",
)

from app.api.exceptions import BaseAPIException


class UserNotFoundError(BaseError):
    pass


class UserNotFoundResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_404_NOT_FOUND])
    error: UserNotFoundError


class UserNotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    model = UserNotFoundResponseModel


class UserConflictError(BaseError):
    pass


class UserConflictResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_409_CONFLICT])
    error: UserConflictError


class UserConflictException(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    model = UserConflictResponseModel


class UserBadRequestError(BaseError):
    pass


class UserBadRequestResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_400_BAD_REQUEST])
    error: UserBadRequestError


class UserBadRequestException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    model = UserBadRequestResponseModel

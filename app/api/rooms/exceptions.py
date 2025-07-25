from fastapi import status
from pydantic import Field

from app.api.base_schemas import BaseError, BaseResponse

__all__ = (
    "RoomNotFoundException",
    "UserNotInRoomException",
    "UserAlreadyInRoomException",
    "RoomNotFoundByInviteCodeException"
)

from app.api.exceptions import BaseAPIException


class RoomNotFoundError(BaseError):
    pass


class RoomNotFoundResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_404_NOT_FOUND])
    error: RoomNotFoundError


class RoomNotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    model = RoomNotFoundResponseModel


class UserNotInRoomError(BaseError):
    pass


class UserNotInRoomResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_403_FORBIDDEN])
    error: UserNotInRoomError


class UserNotInRoomException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    model = UserNotInRoomResponseModel


class RoomNotFoundByInviteCodeError(BaseError):
    pass


class RoomNotFoundByInviteCodeResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_404_NOT_FOUND])
    error: RoomNotFoundByInviteCodeError


class RoomNotFoundByInviteCodeException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    model = RoomNotFoundByInviteCodeResponseModel


class UserAlreadyInRoomError(BaseError):
    pass


class UserAlreadyInRoomResponseModel(BaseResponse):
    status: int = Field(..., examples=[status.HTTP_409_CONFLICT])
    error: UserAlreadyInRoomError


class UserAlreadyInRoomException(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    model = UserAlreadyInRoomResponseModel

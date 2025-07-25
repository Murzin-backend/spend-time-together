from app.core.exceptions import SpendTimeTogetherCoreException


class RoomsServiceError(SpendTimeTogetherCoreException):
    pass


class RoomNotFound(RoomsServiceError):
    msg_template = "Room with id={room_id} not found."


class UserNotInRoom(RoomsServiceError):
    msg_template = "User with id={user_id} is not in room with id={room_id}."


class RoomNotFoundByInviteCode(RoomsServiceError):
    msg_template = "Room with invite code={invite_code} not found."


class UserAlreadyInRoom(RoomsServiceError):
    msg_template = "User with id={user_id} is already in room with id={room_id}."

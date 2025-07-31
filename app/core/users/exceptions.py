from app.core.exceptions import SpendTimeTogetherCoreException


class UsersServiceError(SpendTimeTogetherCoreException):
    pass


class UserNotFound(UsersServiceError):
    msg_template = "User with id={user_id} not found."


class LoginAlreadyExists(UsersServiceError):
    msg_template = "User with login={login} already exists."


class EmailAlreadyExists(UsersServiceError):
    msg_template = "User with email={email} already exists."


class AvatarException(UsersServiceError):
    pass


class InvalidAvatarFormatException(AvatarException):
    msg_template = "Invalid avatar format: {detail}"


class AvatarTooLargeException(AvatarException):
    msg_template = "Avatar is too large: {detail}"

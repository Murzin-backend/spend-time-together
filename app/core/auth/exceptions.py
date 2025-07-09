from app.core.exceptions import SpendTimeTogetherCoreException


class AuthServiceError(SpendTimeTogetherCoreException):
    pass


class UserNotFound(AuthServiceError):
    msg_template = "User with login={login} not found."


class IncorrectPassword(AuthServiceError):
    msg_template = "Incorrect password for user with login={login}."


class UserAlreadyExists(AuthServiceError):
    msg_template = "User with login={login} or email={email} already exists."


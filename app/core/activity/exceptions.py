from app.core.exceptions import SpendTimeTogetherCoreException


class ActivityServiceError(SpendTimeTogetherCoreException):
    pass


class ActivityNotFound(ActivityServiceError):
    msg_template = "Activity with id={activity_id} not found."


class ActivityNotInProgress(ActivityServiceError):
    msg_template = "Activity with id={activity_id} not in progress."


class UserAlreadySubmittedVariant(ActivityServiceError):
    msg_template = "User with id={user_id} already submitted variant for activity with id={activity_id}."
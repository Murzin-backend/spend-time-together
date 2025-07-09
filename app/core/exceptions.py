from enum import Enum
from typing import Any


class SpendTimeTogetherCoreException(Exception):
    msg_template: str

    def __init__(self, **ctx: Any) -> None:
        self.__dict__ = ctx

    def __str__(self) -> str:
        message_arguments = _prepare_message_args(self.__dict__)
        return self.msg_template.format(**message_arguments)


def _prepare_message_args(arguments: dict[str, Any]) -> dict[str, Any]:
    for key in arguments:
        if isinstance(arguments[key], Enum):
            arguments[key] = arguments[key].value
    return arguments

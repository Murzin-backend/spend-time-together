from typing import TypedDict, Literal


class HeaderDescription(TypedDict):
    description: str
    type: Literal["string", "integer", "number", "boolean", "array", "object"]

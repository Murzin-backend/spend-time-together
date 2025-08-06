from dataclasses import dataclass, field
from datetime import datetime


@dataclass(kw_only=True)
class UserDTO:
    id: int
    login: str
    email: str
    first_name: str
    created_at: datetime
    updated_at: datetime
    last_name: str | None = None
    password: str | None = None
    avatar_url: str | None = None
    telegram_link: str | None = None


@dataclass(kw_only=True)
class UserUpdateDTO:
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    telegram_link: str | None = None

from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class UserDTO:
    id: int
    login: str
    email: str
    first_name: str
    last_name: str
    password: str
    created_at: datetime
    updated_at: datetime

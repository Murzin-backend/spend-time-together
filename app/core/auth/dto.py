from dataclasses import dataclass


@dataclass
class UsersSessionDTO:
    id: int
    user_id: int
    session_token: str
    created_at: str
    updated_at: str


@dataclass
class UserRegistrationDTO:
    id: int
    login: str
    first_name: str
    last_name: str
    email: str
    session_token: str
    created_at: str
    updated_at: str

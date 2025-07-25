from dataclasses import dataclass


@dataclass(kw_only=True)
class RoomDTO:
    id: int
    name: str
    created_at: str
    description: str | None = None


@dataclass(kw_only=True)
class InviteCodeDTO:
    invite_code: str
    room_id: int
    expires_at: str


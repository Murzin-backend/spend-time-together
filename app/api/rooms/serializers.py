from pydantic import BaseModel


class RoomInfoSerializer(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: str

    class Config:
        from_attributes = True


class RoomCreateSerializer(BaseModel):
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class InviteCodeSerializer(BaseModel):
    invite_code: str
    room_id: int
    expires_at: str

    class Config:
        from_attributes = True

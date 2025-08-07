from datetime import datetime

from pydantic import BaseModel

from app.core.activity.constants import ActivityStatuses, ActivityTypes


class ActivitySerializer(BaseModel):
    id: int
    name: str
    room_id: int
    status: ActivityStatuses
    type: ActivityTypes
    creator_user_id: int
    scheduled_at: datetime | None
    winner_user_id: int | None = None

    class Config:
        from_attributes = True


class CreateActivitySerializer(BaseModel):
    name: str
    status: ActivityStatuses
    type: ActivityTypes = ActivityTypes.VIDEO_GAMES
    scheduled_at: str | None
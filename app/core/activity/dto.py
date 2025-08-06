from dataclasses import dataclass
from datetime import datetime

from app.core.activity.constants import ActivityStatuses, ActivityTypes


@dataclass
class ActivityDTO:
    id: int
    name: str
    room_id: int
    creator_user_id: int
    status: ActivityStatuses
    type: ActivityTypes
    scheduled_at: datetime | None
    winner_user_id: int | None = None


@dataclass
class CreateActivityDTO:
    name: str
    status: ActivityStatuses
    scheduled_at: str | None
    type: ActivityTypes = ActivityTypes.VIDEO_GAMES


@dataclass
class UserActivityVariantDTO:
    user_id: int
    activity_id: int
    variant: str

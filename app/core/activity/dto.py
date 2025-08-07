from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from app.core.activity.constants import ActivityStatuses, ActivityTypes


@dataclass
class CreateActivityDTO:
    name: str
    type: ActivityTypes
    status: ActivityStatuses = ActivityStatuses.PLANNED
    scheduled_at: datetime | None = None


@dataclass
class ActivityDTO:
    id: int
    name: str
    room_id: int
    status: ActivityStatuses
    type: ActivityTypes
    scheduled_at: str | None = None
    winner_user_id: int | None = None
    creator_user_id: int | None = None


@dataclass
class GameStoreDTO:
    store_id: int
    store_name: str
    store_url: str | None =  None


@dataclass
class GamePlatformDTO:
    platform_id: int
    platform_name: str
    platform_slug: str | None = None


@dataclass
class UserActivityVariantDTO:
    user_id: int
    activity_id: int
    variant: str
    api_game_id: int
    name: str
    description: str | None = None
    background_image: str | None = None
    background_image_additional: str | None = None
    release_date: datetime | None = None
    rating: str | None =  None
    metacritic: int | None =  None
    stores: List[GameStoreDTO] | None =  None
    platforms: List[GamePlatformDTO] | None =  None

    def __post_init__(self):
        if self.stores is None:
            self.stores = []
        if self.platforms is None:
            self.platforms = []

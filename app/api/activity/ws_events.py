from pydantic import BaseModel
from typing import Optional, List


class UserData(BaseModel):
    id: int
    first_name: str
    last_name: str
    avatar_url: str | None = None


class StoreData(BaseModel):
    store_id: int
    store_name: str
    store_url: str | None = None


class PlatformData(BaseModel):
    platform_id: int
    platform_name: str
    platform_slug: str | None = None


class VariantData(BaseModel):
    user_id: int
    activity_id: int
    variant: str
    api_game_id: int | None = None
    name: str
    description: str | None = None
    background_image: str | None = None
    background_image_additional: str | None = None
    release_date: str | None = None
    rating: str | None = None
    metacritic: int | None = None
    stores: list[StoreData] = []
    platforms: list[PlatformData] = []
    user_first_name: str | None = None
    user_last_name: str | None = None
    user_avatar_url: str | None = None


class ActivityStateEvent(BaseModel):
    event: str = "activity_state"
    status: str
    winner_id: int | None = None
    creator_id: int | None = None


class UsersInActivityEvent(BaseModel):
    event: str = "users_in_activity"
    users: list[UserData]


class ActivityVariantsEvent(BaseModel):
    event: str = "activity_variants"
    variants: list[VariantData]


class ConnectedEvent(BaseModel):
    event: str = "connected"
    data: dict


class UserJoinedEvent(BaseModel):
    event: str = "user_joined"
    user_id: int
    username: str
    avatar_url: str | None = None


class UserLeftEvent(BaseModel):
    event: str = "user_left"
    user_id: int
    username: str


class ActivityStateChangedEvent(BaseModel):
    event: str = "activity_state_changed"
    status: str


class VariantSubmittedEvent(BaseModel):
    event: str = "variant_submitted"
    user_id: int
    variant: str
    username: str
    avatar_url: str | None = None
    game_image: str | None = None
    metacritic: int | None = None


class ReactionEvent(BaseModel):
    event: str = "reaction"
    user_id: int
    username: str
    avatar_url: str | None = None
    reaction_id: str


class RouletteStartedEvent(BaseModel):
    event: str = "roulette_started"
    variants_count: int


class RoulettePreEliminateEvent(BaseModel):
    event: str = "roulette_pre_eliminate"
    user_id: int
    variant: str


class VariantEliminatedEvent(BaseModel):
    event: str = "variant_eliminated"
    user_id: int
    variant: str


class WinnerDeclaredEvent(BaseModel):
    event: str = "winner_declared"
    user_id: int
    variant: str


class RouletteCancelledEvent(BaseModel):
    event: str = "roulette_cancelled"
    reason: str


class ErrorEvent(BaseModel):
    event: str = "error"
    message: str


class PongEvent(BaseModel):
    event: str = "pong"


ALLOWED_REACTIONS = [
    "greeting", "well_played", "thanks",
    "oops", "threaten", "wow"
]

from datetime import datetime

from sqlalchemy import DateTime, func, Enum, ForeignKey, Text
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.activity.constants import ActivityStatuses, ActivityTypes
from app.infra.adapters.database import Base


class Activity(Base):
    __tablename__ = "activity"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"),
        nullable=False
    )
    creator_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    winner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        default=None
    )
    winner_variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_activity_variants.id"),
        nullable=True,
        default=None
    )
    status: Mapped[ActivityStatuses] = mapped_column(
        Enum(ActivityStatuses),
        nullable=False,
        default=ActivityStatuses.PLANNED
    )
    type: Mapped[ActivityTypes] = mapped_column(
        Enum(ActivityTypes),
        nullable=False
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class UserActivity(Base):
    __tablename__ = "user_activity"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
        nullable=False
    )
    activity_id: Mapped[int] = mapped_column(
        ForeignKey(Activity.id),
        primary_key=True,
        nullable=False
    )
    connections_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class UserActivityVariants(Base):
    __tablename__ = "user_activity_variants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    api_game_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
    )
    background_image: Mapped[str] = mapped_column(String(1024), nullable=True)
    background_image_additional: Mapped[str] = mapped_column(String(1024), nullable=True)
    release_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    rating: Mapped[str] = mapped_column(String(4), nullable=True)
    metacritic: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activity.id"),
        nullable=False
    )
    variant: Mapped[str] = mapped_column(String(255), nullable=False)


class GameStore(Base):
    __tablename__ = "game_stores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("user_activity_variants.id"),
        nullable=False
    )
    store_id: Mapped[int] = mapped_column(Integer, nullable=False) 
    store_name: Mapped[str] = mapped_column(String(100), nullable=False) 
    store_url: Mapped[str] = mapped_column(String(1024), nullable=True) 


class GamePlatform(Base):
    __tablename__ = "game_platforms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("user_activity_variants.id"),
        nullable=False
    )
    platform_id: Mapped[int] = mapped_column(Integer, nullable=False) 
    platform_name: Mapped[str] = mapped_column(String(100), nullable=False) 
    platform_slug: Mapped[str] = mapped_column(String(100), nullable=True)


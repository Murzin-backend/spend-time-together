from datetime import datetime

from sqlalchemy import DateTime, func, Enum, ForeignKey
from sqlalchemy import String
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
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class UserActivityVariants(Base):
    __tablename__ = "user_activity_variants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activity.id"),
        nullable=False
    )
    variant: Mapped[str] = mapped_column(String(255), nullable=False)

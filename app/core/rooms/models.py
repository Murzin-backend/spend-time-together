from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.users.models import Users
from app.infra.adapters.database import Base


class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UsersRooms(Base):
    __tablename__ = "users_rooms"

    user_id: Mapped[int] = mapped_column(
        ForeignKey(Users.id),
        primary_key=True,
        nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey(Rooms.id),
        primary_key=True,
        nullable=False
    )


class RoomInvites(Base):
    __tablename__ = "room_invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey(Rooms.id),
        nullable=False
    )
    invite_code: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

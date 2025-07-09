from datetime import datetime

from sqlalchemy import DateTime, func, VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.users.models import Users
from app.infra.adapters.database import Base


class UsersSession(Base):
    __tablename__ = "users_session"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(Users.id),
        nullable=False
    )
    session_token: Mapped[str] = mapped_column(
        VARCHAR(length=255),
        unique=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"UsersSession(id={self.id}, session_token={self.session_token}, user_id={self.user_id})"
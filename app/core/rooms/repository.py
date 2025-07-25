from dataclasses import dataclass

from sqlalchemy import select, func, text

from app.core.mixins import BaseRepository
from app.core.rooms.constants import INVITE_CODE_EXPIRED_PERIOD
from app.core.rooms.models import Rooms, UsersRooms, RoomInvites


@dataclass
class RoomRepository(BaseRepository):
    async def get_rooms_by_user_id(self, user_id: int) -> list[Rooms]:
        query = select(Rooms).join(UsersRooms, UsersRooms.room_id == Rooms.id).where(
            UsersRooms.user_id == user_id
        )
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def create_room(
        self,
        user_id: int,
        name: str,
        description: str | None = None
    ) -> Rooms:
        room = Rooms(name=name, description=description)
        async with self.db.session() as session:
            session.add(room)
            await session.flush()
            user_room = UsersRooms(user_id=user_id, room_id=room.id)
            session.add(user_room)
            await session.commit()
            await session.refresh(room)
            return room

    async def get_room_by_id(self, room_id: int) -> Rooms | None:
        query = select(Rooms).where(Rooms.id == room_id)
        async with self.db.session() as session:
            result = await session.execute(query)
            room = result.scalars().first()
            return room if room is not None else None


    async def is_user_in_room(
        self,
        user_id: int,
        room_id: int
    ) -> bool:
        query = select(UsersRooms).where(
            UsersRooms.user_id == user_id,
            UsersRooms.room_id == room_id
        )
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().first() is not None

    async def create_invite_code(
        self,
        room_id: int,
        invite_code: str
    ) -> RoomInvites:
        expires_at_clause = func.date_add(
            func.now(), text(f"INTERVAL {INVITE_CODE_EXPIRED_PERIOD} DAY")
        )

        room_invites = RoomInvites(
            room_id=room_id,
            invite_code=invite_code,
            expires_at=expires_at_clause
        )
        async with self.db.session() as session:
            session.add(room_invites)
            await session.commit()
            await session.refresh(room_invites)
            return room_invites


    async def get_room_by_invite_code(
        self,
        invite_code: str
    ) -> RoomInvites | None:
        query = select(RoomInvites).where(
            RoomInvites.invite_code == invite_code, RoomInvites.expires_at > func.now()
        )
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def add_user_to_room(
        self,
        user_id: int,
        room_id: int
    ) -> None:
        user_room = UsersRooms(user_id=user_id, room_id=room_id)
        async with self.db.session() as session:
            session.add(user_room)
            await session.commit(
    )

import secrets
import string
from dataclasses import dataclass

from app.core.rooms.dto import RoomDTO, InviteCodeDTO
from app.core.rooms.exceptions import RoomNotFound, UserNotInRoom, RoomNotFoundByInviteCode, UserAlreadyInRoom
from app.core.rooms.repository import RoomRepository


def _generate_invite_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@dataclass
class RoomService:
    room_repository: RoomRepository

    async def get_rooms_by_user_id(self, user_id: int) -> list[RoomDTO]:
        room_models = await self.room_repository.get_rooms_by_user_id(user_id=user_id)
        return [
            RoomDTO(
                id=room.id,
                name=room.name,
                description=room.description,
                created_at=room.created_at.isoformat(),
            ) for room in room_models
        ]

    async def create_room(
        self,
        user_id: int,
        name: str,
        description: str | None = None
    ) -> RoomDTO:
        room_model = await self.room_repository.create_room(
            user_id=user_id,
            name=name,
            description=description
        )
        return RoomDTO(
            id=room_model.id,
            name=room_model.name,
            description=room_model.description,
            created_at=room_model.created_at.isoformat(),
        )

    async def get_room_by_id(self, room_id: int) -> RoomDTO | None:
        room_model = await self.room_repository.get_room_by_id(room_id=room_id)
        if room_model is None:
            return None
        return RoomDTO(
            id=room_model.id,
            name=room_model.name,
            description=room_model.description,
            created_at=room_model.created_at.isoformat(),
        )

    async def create_invite_code(
        self,
        room_id: int,
        user_id: int
    ) -> InviteCodeDTO:
        await self.validate_users_room(room_id=room_id, user_id=user_id)

        invite_code = _generate_invite_code()
        room_invites = await self.room_repository.create_invite_code(
            room_id=room_id,
            invite_code=invite_code
        )

        return InviteCodeDTO(
            invite_code=room_invites.invite_code,
            room_id=room_invites.room_id,
            expires_at=room_invites.expires_at.isoformat()
        )

    async def activate_invite_code(
        self,
        invite_code: str,
        user_id: int
    ) -> RoomDTO:
        room_invite = await self.room_repository.get_room_by_invite_code(invite_code=invite_code)
        if room_invite is None:
            raise RoomNotFoundByInviteCode(invite_code=invite_code)

        room_model = await self.room_repository.get_room_by_id(room_id=room_invite.room_id)
        if room_model is None:
            raise RoomNotFound(room_id=room_invite.room_id)

        if await self.room_repository.is_user_in_room(
            room_id=room_invite.room_id,
            user_id=user_id
        ):
            raise UserAlreadyInRoom(room_id=room_invite.room_id, user_id=user_id)

        await self.room_repository.add_user_to_room(room_id=room_invite.room_id, user_id=user_id)

        return RoomDTO(
            id=room_model.id,
            name=room_model.name,
            description=room_model.description,
            created_at=room_model.created_at.isoformat(),
        )

    async def validate_users_room(
        self,
        room_id: int,
        user_id: int
    ) -> None:
        if not self.get_room_by_id(room_id=room_id):
            raise RoomNotFound(id=room_id)

        if not await self.room_repository.is_user_in_room(
            room_id=room_id,
            user_id=user_id
        ):
            raise UserNotInRoom(room_id=room_id, user_id=user_id)


    async def get_users_in_room(
        self,
        room_id: int,
        user_id: int
    ) -> list[int]:
        await self.validate_users_room(room_id=room_id, user_id=user_id)
        return await self.room_repository.get_users_by_room_id(room_id=room_id)




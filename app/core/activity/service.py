from dataclasses import dataclass

from app.core.activity.constants import ActivityStatuses
from app.core.activity.dto import ActivityDTO, CreateActivityDTO, UserActivityVariantDTO
from app.core.activity.exceptions import ActivityNotFound, ActivityNotInProgress, UserAlreadySubmittedVariant
from app.core.activity.models import UserActivity, UserActivityVariants
from app.core.activity.repository import ActivityRepository
from app.core.rooms.service import RoomService


@dataclass
class ActivityService:
    activity_repository: ActivityRepository
    room_service: RoomService

    async def get_activities_by_room_id(
        self,
        room_id: int,
        user_id: int
    ) -> list[ActivityDTO]:
        await self.room_service.validate_users_room(room_id=room_id, user_id=user_id)


        activities = await self.activity_repository.get_activities_by_room_id(room_id=room_id)
        return [
            ActivityDTO(
                id=activity.id,
                name=activity.name,
                room_id=activity.room_id,
                status=activity.status,
                type=activity.type,
                scheduled_at=activity.scheduled_at.__str__() if activity.scheduled_at else None,
                winner_user_id=activity.winner_user_id
            ) for activity in activities
        ]

    async def get_activity_by_id(self, activity_id: int) -> ActivityDTO:
        activity = await self.activity_repository.get_activity_by_id(activity_id)
        if not activity:
            raise ActivityNotFound(activity_id=activity_id)

        return ActivityDTO(
            id=activity.id,
            name=activity.name,
            room_id=activity.room_id,
            status=activity.status,
            type=activity.type,
            scheduled_at=activity.scheduled_at.__str__() if activity.scheduled_at else None,
            winner_user_id=activity.winner_user_id
        )

    async def create_activity(
        self,
        room_id: int,
        user_id: int,
        activity_dto: CreateActivityDTO
    ) -> ActivityDTO:
        await self.room_service.validate_users_room(room_id=room_id, user_id=user_id)

        created_activity = await self.activity_repository.create_activity(activity_dto=activity_dto, room_id=room_id)

        return ActivityDTO(
            id=created_activity.id,
            name=created_activity.name,
            room_id=created_activity.room_id,
            status=created_activity.status,
            type=created_activity.type,
            scheduled_at=created_activity.scheduled_at if created_activity.scheduled_at else None,
            winner_user_id=created_activity.winner_user_id
        )

    async def join_activity(self, user_id: int, activity_id: int) -> UserActivity:
        activity = await self.activity_repository.get_activity_by_id(activity_id)
        if not activity:
            raise ActivityNotFound(activity_id=activity_id)

        if activity.status != ActivityStatuses.IN_PROGRESS:
            raise ActivityNotInProgress(activity_id=activity_id)

        return await self.activity_repository.add_user_to_activity(
            user_id=user_id,
            activity_id=activity_id
        )

    async def submit_variant(self, user_id: int, activity_id: int, variant: str) -> UserActivityVariants:
        activity = await self.activity_repository.get_activity_by_id(activity_id)
        if not activity:
            raise ActivityNotFound(activity_id=activity_id)

        if activity.status != ActivityStatuses.IN_PROGRESS:
            raise ActivityNotInProgress(activity_id=activity_id)

        existing_variants = await self.get_activity_variants(activity_id)
        if any(v.user_id == user_id for v in existing_variants):
            raise UserAlreadySubmittedVariant(activity_id=activity_id, user_id=user_id)

        return await self.activity_repository.add_user_variant(
            user_id=user_id,
            activity_id=activity_id,
            variant=variant
        )

    async def get_activity_variants(self, activity_id: int) -> list[UserActivityVariantDTO]:
        variants = await self.activity_repository.get_variants_by_activity_id(activity_id)
        return [
            UserActivityVariantDTO(
                user_id=v.user_id,
                activity_id=v.activity_id,
                variant=v.variant
            ) for v in variants
        ]

    async def finalize_activity(self, activity_id: int, winner_user_id: int):
        await self.activity_repository.update_activity_winner_and_status(
            activity_id=activity_id,
            winner_user_id=winner_user_id,
            status=ActivityStatuses.FINISHED
        )

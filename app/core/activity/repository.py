from dataclasses import dataclass

from sqlalchemy import select, func

from app.core.activity.constants import ActivityStatuses
from app.core.activity.dto import ActivityDTO, CreateActivityDTO
from app.core.activity.models import Activity
from app.core.activity.models import UserActivity, UserActivityVariants
from app.core.mixins import BaseRepository


@dataclass
class ActivityRepository(BaseRepository):
    async def remove_user_from_activity(
        self,
        user_id: int,
        activity_id: int
    ):
        query = (
            select(UserActivity)
            .where(UserActivity.user_id == user_id, UserActivity.activity_id == activity_id)
        )
        async with self.db.session() as session:
            result = await session.execute(query)
            user_activity = result.scalars().first()
            if user_activity:
                await session.delete(user_activity)
                await session.commit()

    async def get_users_by_activity_id(
        self,
        activity_id: int
    ) -> list[UserActivity]:
        query = select(UserActivity).where(UserActivity.activity_id == activity_id)

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def get_activities_by_room_id(
        self,
        room_id: int
    ) -> list[Activity]:
        query = select(Activity).where(Activity.room_id == room_id)

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def get_activity_by_id(self, activity_id: int) -> Activity | None:
        query = select(Activity).where(Activity.id == activity_id)
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def create_activity(
        self,
        activity_dto: CreateActivityDTO,
        room_id: int,
        creator_user_id: int
    ) -> Activity:

        activity = Activity(
            name=activity_dto.name,
            room_id=room_id,
            status=activity_dto.status,
            type=activity_dto.type,
            creator_user_id=creator_user_id,
            scheduled_at=activity_dto.scheduled_at or func.now(),
        )

        async with self.db.session() as session:
            session.add(activity)
            await session.commit()
            await session.refresh(activity)
            return activity

    async def add_user_to_activity(self, user_id: int, activity_id: int) -> UserActivity:
        user_activity = UserActivity(user_id=user_id, activity_id=activity_id)
        async with self.db.session() as session:
            session.add(user_activity)
            await session.commit()
            await session.refresh(user_activity)
            return user_activity

    async def add_user_variant(self, user_id: int, activity_id: int, variant: str) -> UserActivityVariants:
        user_variant = UserActivityVariants(user_id=user_id, activity_id=activity_id, variant=variant)
        async with self.db.session() as session:
            session.add(user_variant)
            await session.commit()
            await session.refresh(user_variant)
            return user_variant

    async def get_variants_by_activity_id(self, activity_id: int) -> list[UserActivityVariants]:
        query = select(UserActivityVariants).where(UserActivityVariants.activity_id == activity_id)
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def update_activity_winner_and_status(
        self,
        activity_id: int,
        winner_user_id: int,
        status: ActivityStatuses
    ) -> None:
        query = (
            select(Activity)
            .where(Activity.id == activity_id)
        )
        async with self.db.session() as session:
            result = await session.execute(query)
            activity = result.scalars().one()
            activity.winner_user_id = winner_user_id
            activity.status = status
            await session.commit()

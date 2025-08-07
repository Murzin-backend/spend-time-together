from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional

from sqlalchemy import select, func, update
from sqlalchemy.orm import joinedload

from app.core.activity.constants import ActivityStatuses
from app.core.activity.dto import ActivityDTO, CreateActivityDTO
from app.core.activity.models import Activity
from app.core.activity.models import UserActivity, UserActivityVariants, GameStore, GamePlatform
from app.core.mixins import BaseRepository


@dataclass
class ActivityRepository(BaseRepository):
    async def update_activity_status(
        self,
        activity_id: int,
        status: ActivityStatuses
    ):
        query = (
            select(Activity)
            .where(Activity.id == activity_id)
        )
        async with self.db.session() as session:
            result = await session.execute(query)
            activity = result.scalars().one()
            activity.status = status
            await session.commit()

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

    async def add_user_to_activity(self, user_id: int, activity_id: int) -> Tuple[UserActivity, bool]:
        """
        Добавляет пользователя к активности или увеличивает счетчик подключений,
        если пользователь уже присоединился к активности.

        Возвращает кортеж (UserActivity, is_new_connection), где:
        - UserActivity - объект пользовательской активности
        - is_new_connection - True, если это первое подключение пользователя, False если он уже был подключен
        """
        query = select(UserActivity).where(
            UserActivity.user_id == user_id,
            UserActivity.activity_id == activity_id
        )

        async with self.db.session() as session:
            result = await session.execute(query)
            user_activity = result.scalars().first()
            is_new_connection = False

            if user_activity:
                user_activity.connections_count += 1
            else:
                user_activity = UserActivity(
                    user_id=user_id,
                    activity_id=activity_id,
                    connections_count=1
                )
                session.add(user_activity)
                is_new_connection = True

            await session.commit()
            await session.refresh(user_activity)
            return user_activity, is_new_connection

    async def decrease_user_connections_count(
        self,
        user_id: int,
        activity_id: int
    ) -> bool:
        """
        Уменьшает счетчик подключений пользователя к активности.
        Возвращает True, если запись была удалена (счетчик стал 0).
        """
        query = select(UserActivity).where(
            UserActivity.user_id == user_id,
            UserActivity.activity_id == activity_id
        )

        async with self.db.session() as session:
            result = await session.execute(query)
            user_activity = result.scalars().first()

            if not user_activity:
                return False

            user_activity.connections_count -= 1

            if user_activity.connections_count <= 0:
                await session.delete(user_activity)
                was_deleted = True
            else:
                was_deleted = False

            await session.commit()
            return was_deleted

    async def add_user_variant(
        self,
        user_id: int,
        activity_id: int,
        variant: str,
        api_game_id: int,
        name: str,
        description: Optional[str] = None,
        background_image: Optional[str] = None,
        background_image_additional: Optional[str] = None,
        release_date: Optional[str] = None,
        rating: Optional[str] = None,
        metacritic: Optional[int] = None,
        stores_data: List[dict] = None,
        platforms_data: List[dict] = None
    ) -> UserActivityVariants:
        release_datetime = None
        if release_date:
            try:
                release_datetime = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass

        user_variant = UserActivityVariants(
            user_id=user_id,
            activity_id=activity_id,
            variant=variant,
            api_game_id=api_game_id,
            name=name,
            description=description,
            background_image=background_image,
            background_image_additional=background_image_additional,
            release_date=release_datetime,
            rating=str(rating) if rating else None,
            metacritic=metacritic
        )

        async with self.db.session() as session:
            session.add(user_variant)
            await session.flush()

            if stores_data:
                for store_data in stores_data:
                    store = store_data.get("store", {})
                    store_obj = GameStore(
                        variant_id=user_variant.id,
                        store_id=store.get("id", 0),
                        store_name=store.get("name", "Unknown"),
                        store_url=store_data.get("url")
                    )
                    session.add(store_obj)

            if platforms_data:
                for platform_data in platforms_data:
                    platform = platform_data.get("platform", {})
                    platform_obj = GamePlatform(
                        variant_id=user_variant.id,
                        platform_id=platform.get("id", 0),
                        platform_name=platform.get("name", "Unknown"),
                        platform_slug=platform.get("slug")
                    )
                    session.add(platform_obj)

            await session.commit()
            await session.refresh(user_variant)
            return user_variant

    async def get_variants_with_related_by_activity_id(
        self,
        activity_id: int
    ) -> List[Tuple[UserActivityVariants, List[GameStore], List[GamePlatform]]]:
        """Получает варианты с связанными магазинами и платформами."""
        async with self.db.session() as session:
            variants_query = select(UserActivityVariants).where(
                UserActivityVariants.activity_id == activity_id
            )
            result = await session.execute(variants_query)
            variants = result.scalars().all()

            result_list = []
            for variant in variants:
                stores_query = select(GameStore).where(GameStore.variant_id == variant.id)
                stores_result = await session.execute(stores_query)
                stores = stores_result.scalars().all()

                platforms_query = select(GamePlatform).where(GamePlatform.variant_id == variant.id)
                platforms_result = await session.execute(platforms_query)
                platforms = platforms_result.scalars().all()

                result_list.append((variant, stores, platforms))

            return result_list

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

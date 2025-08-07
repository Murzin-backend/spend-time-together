from dataclasses import dataclass
from typing import Tuple

from app.core.activity.constants import ActivityStatuses
from app.core.activity.dto import ActivityDTO, CreateActivityDTO, UserActivityVariantDTO, GameStoreDTO, GamePlatformDTO
from app.core.activity.exceptions import ActivityNotFound, ActivityNotInProgress, UserAlreadySubmittedVariant
from app.core.activity.models import UserActivity, UserActivityVariants
from app.core.activity.repository import ActivityRepository
from app.core.rooms.service import RoomService
from app.core.users.dto import UserDTO
from app.core.users.service import UserService


@dataclass
class ActivityService:
    activity_repository: ActivityRepository
    room_service: RoomService
    user_service: UserService

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
                winner_user_id=activity.winner_user_id,
                creator_user_id=activity.creator_user_id
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
            winner_user_id=activity.winner_user_id,
            creator_user_id = activity.creator_user_id
        )

    async def create_activity(
        self,
        room_id: int,
        user_id: int,
        activity_dto: CreateActivityDTO
    ) -> ActivityDTO:
        await self.room_service.validate_users_room(room_id=room_id, user_id=user_id)

        created_activity = await self.activity_repository.create_activity(
            activity_dto=activity_dto,
            room_id=room_id,
            creator_user_id=user_id
        )

        return ActivityDTO(
            id=created_activity.id,
            name=created_activity.name,
            room_id=created_activity.room_id,
            status=created_activity.status,
            type=created_activity.type,
            scheduled_at=created_activity.scheduled_at if created_activity.scheduled_at else None,
            winner_user_id=created_activity.winner_user_id,
            creator_user_id=created_activity.creator_user_id
        )

    async def join_activity(self, user_id: int, activity_id: int) -> Tuple[UserActivity, bool]:
        """
        Присоединяет пользователя к активности или увеличивает счетчик подключений.

        Возвращает кортеж (UserActivity, is_new_connection), где:
        - UserActivity - объект пользовательской активности
        - is_new_connection - True, если это первое подключение пользователя, False если он уже был подключен
        """
        activity = await self.activity_repository.get_activity_by_id(activity_id)
        if not activity:
            raise ActivityNotFound(activity_id=activity_id)

        return await self.activity_repository.add_user_to_activity(
            user_id=user_id,
            activity_id=activity_id
        )

    async def exit_activity(self, user_id: int, activity_id: int) -> bool:
        """
        Уменьшает счетчик подключений пользователя к активности.
        Возвращает True, если пользователь полностью покинул активность (счетчик достиг 0).
        """
        activity = await self.activity_repository.get_activity_by_id(activity_id)
        if not activity:
            raise ActivityNotFound(activity_id=activity_id)

        was_deleted = await self.activity_repository.decrease_user_connections_count(
            user_id=user_id,
            activity_id=activity_id
        )

        return was_deleted

    async def get_users_in_activity(self, activity_id: int) -> list[UserDTO]:
        activity = await self.activity_repository.get_activity_by_id(activity_id)
        if not activity:
            raise ActivityNotFound(activity_id=activity_id)

        users_activity = await self.activity_repository.get_users_by_activity_id(activity_id=activity_id)
        return await self.user_service.get_users_by_ids(user_ids=[ua.user_id for ua in users_activity])


    async def submit_variant(self, user_id: int, activity_id: int, variant_data: dict) -> UserActivityVariants:
        activity = await self.activity_repository.get_activity_by_id(activity_id=activity_id)
        if not activity:
            raise ActivityNotFound(activity_id=activity_id)

        if activity.status == ActivityStatuses.IN_PROGRESS or activity.status == ActivityStatuses.FINISHED:
            raise ActivityNotInProgress(activity_id=activity_id)

        existing_variants = await self.get_activity_variants(activity_id)
        if any(v.user_id == user_id for v in existing_variants):
            raise UserAlreadySubmittedVariant(activity_id=activity_id, user_id=user_id)

        variant = variant_data.get("name", "")
        api_game_id = variant_data.get("id", 0)
        name = variant_data.get("name", "")
        description = variant_data.get("description", "")
        background_image = variant_data.get("background_image", "")
        background_image_additional = variant_data.get("background_image_additional", "")
        release_date = variant_data.get("released")
        rating = variant_data.get("rating")
        metacritic = variant_data.get("metacritic")

        stores_data = variant_data.get("stores", [])
        platforms_data = variant_data.get("platforms", [])

        return await self.activity_repository.add_user_variant(
            user_id=user_id,
            activity_id=activity_id,
            variant=variant,
            api_game_id=api_game_id,
            name=name,
            description=description,
            background_image=background_image,
            background_image_additional=background_image_additional,
            release_date=release_date,
            rating=rating,
            metacritic=metacritic,
            stores_data=stores_data,
            platforms_data=platforms_data
        )

    async def get_activity_variants(self, activity_id: int) -> list[UserActivityVariantDTO]:
        variants_with_related = await self.activity_repository.get_variants_with_related_by_activity_id(activity_id=activity_id)

        result = []
        for variant, stores, platforms in variants_with_related:
            stores_dto = [
                GameStoreDTO(
                    store_id=store.store_id,
                    store_name=store.store_name,
                    store_url=store.store_url
                ) for store in stores
            ]

            platforms_dto = [
                GamePlatformDTO(
                    platform_id=platform.platform_id,
                    platform_name=platform.platform_name,
                    platform_slug=platform.platform_slug
                ) for platform in platforms
            ]

            result.append(
                UserActivityVariantDTO(
                    user_id=variant.user_id,
                    activity_id=variant.activity_id,
                    variant=variant.variant,
                    api_game_id=variant.api_game_id,
                    name=variant.name,
                    description=variant.description,
                    background_image=variant.background_image,
                    background_image_additional=variant.background_image_additional,
                    release_date=variant.release_date,
                    rating=variant.rating,
                    metacritic=variant.metacritic,
                    stores=stores_dto,
                    platforms=platforms_dto
                )
            )

        return result

    async def finalize_activity(self, activity_id: int, winner_user_id: int):
        await self.activity_repository.update_activity_winner_and_status(
            activity_id=activity_id,
            winner_user_id=winner_user_id,
            status=ActivityStatuses.FINISHED
        )

    async def update_activity_status(self, activity_id: int, status: ActivityStatuses):
        await self.activity_repository.update_activity_status(activity_id=activity_id, status=status)

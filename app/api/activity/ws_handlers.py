import asyncio
import logging
import random

from fastapi import WebSocket

from app.core.activity.constants import ActivityStatuses
from app.core.activity.exceptions import ActivityNotFound, ActivityNotInProgress, UserAlreadySubmittedVariant
from app.core.activity.service import ActivityService

from .ws_connection import manager
from .ws_events import (
    UserData, StoreData, PlatformData, VariantData,
    UsersInActivityEvent, ActivityVariantsEvent, ActivityStateChangedEvent,
    VariantSubmittedEvent, ReactionEvent, ErrorEvent, PongEvent,
    RouletteStartedEvent, RoulettePreEliminateEvent, VariantEliminatedEvent,
    WinnerDeclaredEvent, RouletteCancelledEvent,
    ALLOWED_REACTIONS,
)

logger = logging.getLogger(__name__)


async def send_users_in_activity(activity_id: int, activity_service: ActivityService):
    try:
        users = await activity_service.get_users_in_activity(activity_id)
        event = UsersInActivityEvent(
            users=[
                UserData(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    avatar_url=user.avatar_url,
                )
                for user in users
            ]
        )
        await manager.broadcast(event, activity_id)
    except Exception as e:
        logger.error(f"Ошибка при отправке списка пользователей: {e}")


async def send_activity_variants(websocket: WebSocket, activity_id: int, activity_service: ActivityService):
    try:
        variants = await activity_service.get_activity_variants(activity_id)
        variants_data = []
        for v in variants:
            release_date_str = v.release_date.isoformat() if v.release_date else None
            stores = [
                StoreData(store_id=s.store_id, store_name=s.store_name, store_url=s.store_url)
                for s in (v.stores or [])
            ]
            platforms = [
                PlatformData(platform_id=p.platform_id, platform_name=p.platform_name, platform_slug=p.platform_slug)
                for p in (v.platforms or [])
            ]
            variants_data.append(VariantData(
                user_id=v.user_id,
                activity_id=v.activity_id,
                variant=v.variant,
                api_game_id=v.api_game_id,
                name=v.name,
                description=v.description,
                background_image=v.background_image,
                background_image_additional=v.background_image_additional,
                release_date=release_date_str,
                rating=v.rating,
                metacritic=v.metacritic,
                stores=stores,
                platforms=platforms,
                user_first_name=v.user_first_name,
                user_last_name=v.user_last_name,
                user_avatar_url=v.user_avatar_url,
            ))
        event = ActivityVariantsEvent(variants=variants_data)
        await manager.send_personal(event, websocket)
    except Exception as e:
        logger.error(f"Ошибка при отправке вариантов активности: {e}")


async def handle_ping(websocket: WebSocket):
    await manager.send_personal(PongEvent(), websocket)


async def handle_get_users(activity_id: int, activity_service: ActivityService):
    await send_users_in_activity(activity_id, activity_service)


async def handle_get_variants(websocket: WebSocket, activity_id: int, activity_service: ActivityService):
    await send_activity_variants(websocket, activity_id, activity_service)


async def handle_send_reaction(
    websocket: WebSocket,
    activity_id: int,
    user_info,
    payload: dict,
):
    reaction_id = payload.get("reaction_id")
    if reaction_id in ALLOWED_REACTIONS:
        event = ReactionEvent(
            user_id=user_info.id,
            username=user_info.first_name,
            avatar_url=user_info.avatar_url,
            reaction_id=reaction_id,
        )
        await manager.broadcast(event, activity_id)


async def handle_start_game(
    websocket: WebSocket,
    activity_id: int,
    user_info,
    activity,
    activity_service: ActivityService,
):
    if user_info.id != activity.creator_user_id:
        await manager.send_personal(
            ErrorEvent(message="Только создатель активности может запустить игру"),
            websocket,
        )
        return

    try:
        variants = await activity_service.get_activity_variants(activity_id)
        if len(variants) < 2:
            await manager.send_personal(
                ErrorEvent(message="Для начала игры нужно минимум 2 варианта"),
                websocket,
            )
            return

        await activity_service.update_activity_status(
            activity_id=activity_id,
            status=ActivityStatuses.IN_PROGRESS,
        )
        await manager.broadcast(
            ActivityStateChangedEvent(status=ActivityStatuses.IN_PROGRESS),
            activity_id,
        )
        asyncio.create_task(start_roulette(activity_id, activity_service))

    except Exception as e:
        logger.error(f"Ошибка при запуске игры: {e}")
        await manager.send_personal(
            ErrorEvent(message=f"Ошибка при запуске игры: {str(e)}"),
            websocket,
        )


async def handle_submit_variant(
    websocket: WebSocket,
    activity_id: int,
    user_info,
    payload: dict,
    activity_service: ActivityService,
):
    variant_data = payload.get("variant")
    if not variant_data:
        return

    try:
        activity = await activity_service.get_activity_by_id(activity_id)
        if activity.status == ActivityStatuses.IN_PROGRESS:
            await manager.send_personal(
                ErrorEvent(message="Нельзя предлагать варианты после начала игры"),
                websocket,
            )
            return

        variants = await activity_service.get_activity_variants(activity_id)
        if any(v.user_id == user_info.id for v in variants):
            await manager.send_personal(
                ErrorEvent(message="Вы уже предложили вариант для этой активности"),
                websocket,
            )
            return

        await activity_service.submit_variant(
            user_id=user_info.id,
            activity_id=activity_id,
            variant_data=variant_data,
        )
        await manager.broadcast(
            VariantSubmittedEvent(
                user_id=user_info.id,
                variant=variant_data.get("name", ""),
                username=user_info.first_name,
                avatar_url=user_info.avatar_url,
                game_image=variant_data.get("background_image", ""),
                metacritic=variant_data.get("metacritic"),
            ),
            activity_id,
        )

    except (ActivityNotFound, ActivityNotInProgress) as e:
        await manager.send_personal(ErrorEvent(message=str(e)), websocket)
    except UserAlreadySubmittedVariant as e:
        await manager.send_personal(ErrorEvent(message=str(e)), websocket)


async def start_roulette(activity_id: int, activity_service: ActivityService):
    """Run the roulette elimination loop."""
    logger.info(f"Запуск рулетки для активности {activity_id}")

    variants_dto = await activity_service.get_activity_variants(activity_id)

    if not variants_dto or len(variants_dto) < 2:
        logger.warning(f"Недостаточно вариантов для активности {activity_id}")
        await manager.broadcast(
            RouletteCancelledEvent(reason="Необходимо минимум 2 варианта для запуска рулетки"),
            activity_id,
        )
        await activity_service.update_activity_status(
            activity_id=activity_id,
            status=ActivityStatuses.PLANNED,
        )
        return

    variants = list(variants_dto)
    random.shuffle(variants)

    await manager.broadcast(
        RouletteStartedEvent(variants_count=len(variants)),
        activity_id,
    )

    while len(variants) > 1:
        remaining = len(variants)
        if remaining > 4:
            delay, pre_delay = 2, 1
        elif remaining > 2:
            delay, pre_delay = 4, 1.5
        else:
            delay, pre_delay = 6, 2

        eliminated = variants.pop()

        await asyncio.sleep(delay - pre_delay)
        await manager.broadcast(
            RoulettePreEliminateEvent(user_id=eliminated.user_id, variant=eliminated.variant),
            activity_id,
        )

        await asyncio.sleep(pre_delay)
        logger.info(f"Вариант '{eliminated.variant}' от пользователя {eliminated.user_id} выбыл")
        await manager.broadcast(
            VariantEliminatedEvent(user_id=eliminated.user_id, variant=eliminated.variant),
            activity_id,
        )

    winner = variants[0]
    logger.info(f"Победитель активности {activity_id}: пользователь {winner.user_id} с вариантом '{winner.variant}'")

    await asyncio.sleep(3)

    try:
        await activity_service.finalize_activity(activity_id, winner.user_id)
    except Exception as e:
        logger.error(f"Ошибка при финализации активности: {e}")

    await manager.broadcast(
        WinnerDeclaredEvent(user_id=winner.user_id, variant=winner.variant),
        activity_id,
    )

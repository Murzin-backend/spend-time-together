import asyncio
import json
import logging
import random

from dependency_injector.wiring import inject, Provide
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from app.api.auth.deps import get_authenticated_user_for_ws
from app.api.routing import SpendTimeTogetherAPIRoute
from app.core.activity.constants import ActivityStatuses
from app.core.activity.exceptions import ActivityNotFound, ActivityNotInProgress
from app.core.activity.service import ActivityService
from app.core.rooms.exceptions import RoomNotFound, UserNotInRoom
from app.core.rooms.service import RoomService
from app.core.users.service import UserService
from app.di.containers import DIContainer

router = APIRouter(route_class=SpendTimeTogetherAPIRoute)

activity_timers = {}

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int):
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, activity_id: int):
        if activity_id in self.active_connections:
            for connection in self.active_connections[activity_id]:
                await connection.send_text(message)


manager = ConnectionManager()


async def send_users_in_activity(activity_id: int, activity_service: ActivityService):
    """Получает и отправляет список всех пользователей в активности."""
    try:
        users = await activity_service.get_users_in_activity(activity_id)

        users_data = [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "avatar_url": user.avatar_url
            }
            for user in users
        ]

        await manager.broadcast(
            json.dumps({
                "event": "users_in_activity",
                "users": users_data
            }),
            activity_id
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке списка пользователей: {str(e)}")


@router.websocket("/ws/activity/{activity_id}")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    activity_id: int,
    activity_service: ActivityService = Depends(Provide[DIContainer.services.activity_service]),
    room_service: RoomService = Depends(Provide[DIContainer.services.room_service]),
    user_service: UserService = Depends(Provide[DIContainer.services.user_service])
):
    """
    WebSocket эндпоинт для активностей.
    """
    logger.info(f"Попытка подключения к WebSocket для activity_id={activity_id}")

    await websocket.accept()
    logger.info("WebSocket соединение успешно установлено")

    try:
        user_session = await get_authenticated_user_for_ws(websocket=websocket)
        if user_session is None:
            logger.error("Пользователь не аутентифицирован")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
            return

        logger.info(f"Аутентификация пользователя {user_session.user_id} успешна")

        user_info = await user_service.get_user_by_id(user_id=user_session.user_id)
        if user_info is None:
            logger.error(f"Пользователь с ID {user_session.user_id} не найден")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return

        try:
            activity = await activity_service.get_activity_by_id(activity_id)

            if activity.creator_user_id is None:
                await websocket.close(code=4000, reason="Activity creator not found")
                return

            try:
                await room_service.validate_users_room(room_id=activity.room_id, user_id=user_info.id)
            except (RoomNotFound, UserNotInRoom) as e:
                await websocket.close(code=4003, reason=str(e))
                return

            await manager.connect(websocket, activity_id)

            try:
                await activity_service.join_activity(
                    user_id=user_info.id,
                    activity_id=activity_id
                )
            except ActivityNotFound as error:
                logger.error(f"Activity not found: {error}")
                await websocket.close(code=4000, reason="Activity not found")
                return
            except ActivityNotInProgress as error:
                logger.error(f"Activity not in progress: {error}")
                await websocket.close(code=4000, reason="Activity is not in progress")
                return

            await websocket.send_json({
                "event": "activity_state",
                "status": activity.status,
                "winner_id": activity.winner_user_id,
                "creator_id": activity.creator_user_id
            })

            users = await activity_service.get_users_in_activity(activity_id)
            users_data = [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "avatar_url": user.avatar_url
                }
                for user in users
            ]

            await websocket.send_json({
                "event": "users_in_activity",
                "users": users_data
            })

            response = {
                "event": "connected",
                "data": {
                    "message": f"Вы успешно подключились к активности {activity_id}"
                }
            }
            await manager.send_personal_message(json.dumps(response), websocket)

            await manager.broadcast(json.dumps({
                "event": "user_joined",
                "user_id": user_info.id,
                "username": user_info.first_name,
                "avatar_url": user_info.avatar_url
            }), activity_id)

            await send_users_in_activity(activity_id, activity_service)

            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                logger.info(f"Получено сообщение: {message}")

                action = message.get("action")
                payload = message.get("payload", {})

                if action == "ping":
                    await manager.send_personal_message(json.dumps({"event": "pong"}), websocket)

                elif action == "get_users":
                    await send_users_in_activity(activity_id, activity_service)

                elif action == "start_game":
                    if user_info.id == activity.creator_user_id:
                        try:
                            if activity_id not in activity_timers:
                                task = asyncio.create_task(
                                    start_variant_submission_timer(activity_id, activity_service)
                                )
                                activity_timers[activity_id] = task
                                logger.info(f"Таймер для активности {activity_id} запущен")
                            else:
                                logger.info(f"Таймер для активности {activity_id} уже запущен")
                        except (ActivityNotFound, ActivityNotInProgress) as e:
                            await websocket.send_json({
                                "event": "error",
                                "message": str(e)
                            })
                    else:
                        await websocket.send_json({
                            "event": "error",
                            "message": "Только создатель активности может запустить игру"
                        })

                elif action == "submit_variant":
                    variant = payload.get("variant")
                    if variant:
                        try:
                            await activity_service.submit_variant(
                                user_id=user_info.id,
                                activity_id=activity_id,
                                variant=variant,
                            )
                            await manager.broadcast(
                                json.dumps({
                                    "event": "variant_submitted",
                                    "user_id": user_info.id,
                                    "variant": variant,
                                    "username": user_info.first_name,
                                    "avatar_url": user_info.avatar_url
                                }),
                                activity_id
                            )
                        except (ActivityNotFound, ActivityNotInProgress) as e:
                            await websocket.send_json({
                                "event": "error",
                                "message": str(e)
                            })

        except ActivityNotFound:
            await websocket.close(code=4000, reason="Activity not found")
            return

    except WebSocketDisconnect:
        logger.info(f"WebSocket соединение разорвано для activity_id={activity_id}")
        manager.disconnect(websocket, activity_id)
        if 'user_info' in locals() and user_info and activity_id in manager.active_connections:
            try:
                await activity_service.exit_activity(user_id=user_info.id, activity_id=activity_id)
                logger.info(f"Пользователь {user_info.id} удален из активности {activity_id}")
            except Exception as e:
                logger.error(f"Ошибка при удалении пользователя из активности: {str(e)}")

            await manager.broadcast(json.dumps({
                "event": "user_left",
                "user_id": user_info.id,
                "username": user_info.first_name
            }), activity_id)

            await send_users_in_activity(activity_id, activity_service)
    except Exception as e:
        logger.error(f"Ошибка в WebSocket обработчике: {str(e)}")
        await websocket.close(code=4000, reason=str(e))
    finally:
        if 'activity_id' in locals() and activity_id:
            manager.disconnect(websocket, activity_id)
            if activity_id in manager.active_connections and not manager.active_connections[activity_id]:
                if activity_id in activity_timers:
                    activity_timers[activity_id].cancel()
                    del activity_timers[activity_id]


async def start_variant_submission_timer(activity_id: int, activity_service: ActivityService):
    """Запускает таймер на 60 секунд для сбора вариантов."""
    logger.info(f"Начало таймера для активности {activity_id}")
    await manager.broadcast(json.dumps({"event": "timer_started", "duration": 60}), activity_id)

    await asyncio.sleep(60)
    logger.info(f"Таймер для активности {activity_id} завершен")
    await manager.broadcast(json.dumps({"event": "timer_finished"}), activity_id)

    await start_roulette(activity_id, activity_service)

    if activity_id in activity_timers:
        del activity_timers[activity_id]


async def start_roulette(activity_id: int, activity_service: ActivityService):
    """Запускает рулетку для выбора победителя на сервере."""
    logger.info(f"Запуск рулетки для активности {activity_id}")

    variants_dto = await activity_service.get_activity_variants(activity_id)

    if not variants_dto:
        logger.warning(f"Нет вариантов для активности {activity_id}, рулетка отменена")
        await manager.broadcast(
            json.dumps({"event": "roulette_cancelled", "reason": "No variants submitted"}),
            activity_id
        )
        # TODO: Обновить статус активности на CANCELLED
        return

    variants = [v for v in variants_dto]
    random.shuffle(variants)

    await manager.broadcast(
        json.dumps({
            "event": "roulette_started",
            "variants_count": len(variants)
        }),
        activity_id
    )

    while len(variants) > 1:
        await asyncio.sleep(3)
        eliminated = variants.pop()
        logger.info(f"Вариант '{eliminated.variant}' от пользователя {eliminated.user_id} выбыл")
        await manager.broadcast(
            json.dumps({
                "event": "variant_eliminated",
                "user_id": eliminated.user_id,
                "variant": eliminated.variant,
            }),
            activity_id
        )

    winner = variants[0]
    logger.info(f"Победитель активности {activity_id}: пользователь {winner.user_id} с вариантом '{winner.variant}'")

    try:
        await activity_service.finalize_activity(activity_id, winner.user_id)
    except Exception as e:
        logger.error(f"Ошибка при финализации активности: {str(e)}")

    await manager.broadcast(
        json.dumps({
            "event": "winner_declared",
            "user_id": winner.user_id,
            "variant": winner.variant,
        }),
        activity_id
    )

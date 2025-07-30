import asyncio
import json
import random

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.api.auth.deps import get_authenticated_user_for_ws
from app.api.routing import SpendTimeTogetherAPIRoute
from app.core.activity.constants import ActivityStatuses
from app.core.activity.exceptions import ActivityNotFound, ActivityNotInProgress
from app.core.activity.service import ActivityService
from app.core.rooms.exceptions import RoomNotFound, UserNotInRoom
from app.core.rooms.service import RoomService
from app.core.users.dto import UserDTO
from app.di.containers import DIContainer

router = APIRouter(route_class=SpendTimeTogetherAPIRoute)

# Глобальный словарь для отслеживания запущенных таймеров для активностей
activity_timers = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, activity_id: int):
        if activity_id in self.active_connections:
            for connection in self.active_connections[activity_id]:
                await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/activity/{activity_id}")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    activity_id: int,
    current_user: UserDTO = Depends(get_authenticated_user_for_ws),
    activity_service: ActivityService = Depends(Provide[DIContainer.services.activity_service]),
    room_service: RoomService = Depends(Provide[DIContainer.services.room_service])
):
    try:
        activity = await activity_service.get_activity_by_id(activity_id)
        if activity.status != ActivityStatuses.IN_PROGRESS:
            await websocket.close(code=4000, reason="Activity is not in progress")
            return

        try:
            await room_service.validate_users_room(room_id=activity.room_id, user_id=current_user.id)
        except (RoomNotFound, UserNotInRoom) as e:
            await websocket.close(code=4003, reason=str(e))
            return

        await manager.connect(websocket, activity_id)

        # Отправляем текущее состояние активности при подключении
        await websocket.send_json({
            "event": "activity_state",
            "status": activity.status,
            "winner_id": activity.winner_user_id
        })

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            payload = message.get("payload")

            if action == "join":
                try:
                    await activity_service.join_activity(user_id=current_user.id, activity_id=activity_id)
                    await manager.broadcast(json.dumps({"event": "user_joined", "user_id": current_user.id}), activity_id)

                    if activity_id not in activity_timers:
                        task = asyncio.create_task(start_variant_submission_timer(activity_id, activity_service))
                        activity_timers[activity_id] = task
                except (ActivityNotFound, ActivityNotInProgress) as e:
                    await websocket.send_json({
                        "event": "error",
                        "message": str(e)
                    })

            elif action == "submit_variant":
                variant = payload.get("variant")
                if variant:
                    try:
                        await activity_service.submit_variant(
                            user_id=current_user.id,
                            activity_id=activity_id,
                            variant=variant
                        )
                        await manager.broadcast(
                            json.dumps({"event": "variant_submitted", "user_id": current_user.id, "variant": variant}),
                            activity_id
                        )
                    except (ActivityNotFound, ActivityNotInProgress) as e:
                        await websocket.send_json({
                            "event": "error",
                            "message": str(e)
                        })

    except WebSocketDisconnect:
        manager.disconnect(websocket, activity_id)
        await manager.broadcast(json.dumps({"event": "user_left", "user_id": current_user.id}), activity_id)
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))
    finally:
        manager.disconnect(websocket, activity_id)
        if activity_id in manager.active_connections and not manager.active_connections[activity_id]:
            if activity_id in activity_timers:
                activity_timers[activity_id].cancel()
                del activity_timers[activity_id]


async def start_variant_submission_timer(activity_id: int, activity_service: ActivityService):
    """Запускает таймер на 60 секунд для сбора вариантов."""
    await manager.broadcast(json.dumps({"event": "timer_started", "duration": 60}), activity_id)
    await asyncio.sleep(60)
    await manager.broadcast(json.dumps({"event": "timer_finished"}), activity_id)

    # После окончания таймера запускаем логику рулетки
    await start_roulette(activity_id, activity_service)
    # Удаляем таймер из словаря после выполнения
    if activity_id in activity_timers:
        del activity_timers[activity_id]


async def start_roulette(activity_id: int, activity_service: ActivityService):
    """Запускает рулетку для выбора победителя на сервере."""
    variants_dto = await activity_service.get_activity_variants(activity_id)

    if not variants_dto:
        await manager.broadcast(json.dumps({"event": "roulette_cancelled", "reason": "No variants submitted"}), activity_id)
        # TODO: Обновить статус активности на CANCELLED
        return

    variants = [v for v in variants_dto]
    random.shuffle(variants)

    # Выбиваем варианты, пока не останется один
    while len(variants) > 1:
        await asyncio.sleep(3)  # Пауза для драматизма
        eliminated = variants.pop()
        await manager.broadcast(
            json.dumps({
                "event": "variant_eliminated",
                "user_id": eliminated.user_id,
                "variant": eliminated.variant
            }),
            activity_id
        )

    # Объявляем победителя
    winner = variants[0]
    await activity_service.finalize_activity(activity_id, winner.user_id)

    await manager.broadcast(
        json.dumps({
            "event": "winner_declared",
            "user_id": winner.user_id,
            "variant": winner.variant
        }),
        activity_id
    )

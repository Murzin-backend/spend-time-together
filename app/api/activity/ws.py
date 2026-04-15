"""WebSocket endpoint for activity rooms."""
import json
import logging

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
from app.core.activity.exceptions import ActivityNotFound, ActivityNotInProgress
from app.core.activity.service import ActivityService
from app.core.rooms.exceptions import RoomNotFound, UserNotInRoom
from app.core.rooms.service import RoomService
from app.core.users.service import UserService
from app.di.containers import DIContainer

from .ws_connection import manager
from .ws_events import (
    ActivityStateEvent, ConnectedEvent, UserJoinedEvent, UserLeftEvent,
)
from .ws_handlers import (
    send_users_in_activity, send_activity_variants,
    handle_ping, handle_get_users, handle_get_variants,
    handle_send_reaction, handle_start_game, handle_submit_variant,
)

router = APIRouter(route_class=SpendTimeTogetherAPIRoute)

activity_timers = {}

logger = logging.getLogger(__name__)


@router.websocket("/ws/activity/{activity_id}")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    activity_id: int,
    activity_service: ActivityService = Depends(Provide[DIContainer.services.activity_service]),
    room_service: RoomService = Depends(Provide[DIContainer.services.room_service]),
    user_service: UserService = Depends(Provide[DIContainer.services.user_service])
):
    logger.info(f"Попытка подключения к WebSocket для activity_id={activity_id}")
    await websocket.accept()

    try:
        # Authenticate
        user_session = await get_authenticated_user_for_ws(websocket=websocket)
        if user_session is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
            return

        user_info = await user_service.get_user_by_id(user_id=user_session.user_id)
        if user_info is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return

        # Validate activity and room access
        try:
            activity = await activity_service.get_activity_by_id(activity_id)
            if activity.creator_user_id is None:
                await websocket.close(code=4000, reason="Activity creator not found")
                return

            await room_service.validate_users_room(room_id=activity.room_id, user_id=user_info.id)
        except ActivityNotFound:
            await websocket.close(code=4000, reason="Activity not found")
            return
        except (RoomNotFound, UserNotInRoom) as e:
            await websocket.close(code=4003, reason=str(e))
            return

        # Connect
        await manager.connect(websocket, activity_id)

        try:
            user_activity, is_new_connection = await activity_service.join_activity(
                user_id=user_info.id,
                activity_id=activity_id,
            )
        except (ActivityNotFound, ActivityNotInProgress) as e:
            await websocket.close(code=4000, reason=str(e))
            return

        # Send initial state
        await manager.send_personal(
            ActivityStateEvent(
                status=activity.status,
                winner_id=activity.winner_user_id,
                creator_id=activity.creator_user_id,
            ),
            websocket,
        )
        await send_users_in_activity(activity_id, activity_service)
        await send_activity_variants(websocket, activity_id, activity_service)
        await manager.send_personal(
            ConnectedEvent(data={"message": f"Вы успешно подключились к активности {activity_id}"}),
            websocket,
        )

        if is_new_connection:
            await manager.broadcast(
                UserJoinedEvent(
                    user_id=user_info.id,
                    username=user_info.first_name,
                    avatar_url=user_info.avatar_url,
                ),
                activity_id,
            )
            await send_users_in_activity(activity_id, activity_service)

        # Message loop
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            payload = message.get("payload", {})

            if action == "ping":
                await handle_ping(websocket)
            elif action == "get_users":
                await handle_get_users(activity_id, activity_service)
            elif action == "get_variants":
                await handle_get_variants(websocket, activity_id, activity_service)
            elif action == "send_reaction":
                await handle_send_reaction(websocket, activity_id, user_info, payload)
            elif action == "start_game":
                await handle_start_game(websocket, activity_id, user_info, activity, activity_service)
            elif action == "submit_variant":
                await handle_submit_variant(websocket, activity_id, user_info, payload, activity_service)

    except WebSocketDisconnect:
        logger.info(f"WebSocket соединение разорвано для activity_id={activity_id}")
        manager.disconnect(websocket, activity_id)
        if 'user_info' in locals() and user_info and activity_id in manager.active_connections:
            try:
                was_removed = await activity_service.exit_activity(
                    user_id=user_info.id, activity_id=activity_id
                )
                if was_removed:
                    logger.info(f"Пользователь {user_info.id} полностью покинул активность {activity_id}")
                    await manager.broadcast(
                        UserLeftEvent(user_id=user_info.id, username=user_info.first_name),
                        activity_id,
                    )
                    await send_users_in_activity(activity_id, activity_service)
            except Exception as e:
                logger.error(f"Ошибка при обработке отключения пользователя: {e}")

    except Exception as e:
        logger.error(f"Ошибка в WebSocket обработчике: {e}")
        await websocket.close(code=4000, reason=str(e))
    finally:
        if 'activity_id' in locals() and activity_id:
            manager.disconnect(websocket, activity_id)
            if not manager.has_connections(activity_id):
                if activity_id in activity_timers:
                    activity_timers[activity_id].cancel()
                    del activity_timers[activity_id]

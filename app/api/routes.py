from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.api.activity.controller import router as activity_router
from app.api.activity.ws import router as ws_activity_router
from app.api.auth.controller import router as auth_router
from app.api.rooms.controller import router as room_router
from app.api.routing import SpendTimeTogetherAPIRoute
from app.api.users.controller import router as users_router

api_router = APIRouter(
    prefix="/api",
    default_response_class=ORJSONResponse,
    route_class=SpendTimeTogetherAPIRoute
)

api_router.include_router(users_router, tags=["users"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(room_router, tags=["rooms"])
api_router.include_router(activity_router, tags=["activity"])
api_router.include_router(ws_activity_router, tags=["ws_activity"])

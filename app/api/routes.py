from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from app.api.routing import SpendTimeTogetherAPIRoute

from app.api.users.controller import router as users_router

api_router = APIRouter(
    prefix="/api",
    default_response_class=ORJSONResponse,
    route_class=SpendTimeTogetherAPIRoute
)

api_router.include_router(users_router, tags=["users"])

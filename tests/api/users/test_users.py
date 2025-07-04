import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users.models import Users
from tests.factories.users import UserFactory

pytestmark = [pytest.mark.asyncio]


@pytest.mark.parametrize(
    "users_count, expected_status",
    [
        (3, status.HTTP_200_OK),
    ],
)
async def test_get_users_list(
    rest_client: AsyncClient,
    async_session: AsyncSession,
    users_count: int,
    expected_status: int,
) -> None:
    users_data = UserFactory.create_batch_dict(users_count)
    users = [Users(**user) for user in users_data]
    async_session.add_all(users)
    await async_session.commit()

    response = await rest_client.get("/api/users")

    assert response.status_code == expected_status
    response_data = response.json()
    assert response_data["status"] == expected_status
    assert response_data["error"] is None
    assert len(response_data["payload"]["data"]) == users_count

    for user in response_data["payload"]["data"]:
        assert all(
            key in user
            for key in [
                "id",
                "login",
                "email",
                "first_name",
                "last_name",
                "created_at",
                "updated_at",
            ]
        )
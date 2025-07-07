import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.users import UserFactory

pytestmark = [pytest.mark.asyncio]


@pytest.mark.parametrize(
    "users_count, expected_status",
    [
        (3, status.HTTP_200_OK),
        (0, status.HTTP_200_OK),
        (10, status.HTTP_200_OK),
    ],
)
async def test_get_users_list(
    rest_client: AsyncClient,
    db_session: AsyncSession,
    users_count: int,
    expected_status: int,
) -> None:
    UserFactory._meta.sqlalchemy_session = db_session
    await UserFactory.create_batch(users_count)

    response = await rest_client.get("/api/users")

    assert response.status_code == expected_status
    response_data = response.json()
    assert response_data["status"] == expected_status
    assert response_data["error"] is None
    assert len(response_data["payload"]["data"]) == users_count
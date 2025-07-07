from datetime import datetime

import factory
from factory import Faker

from app.core.users.models import Users
from tests.factories.base import AsyncSQLAlchemyModelFactory


class UserFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Users
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    id = factory.Sequence(lambda n: n + 1)
    login = factory.LazyAttribute(lambda obj: f"user_{obj.id}")
    email = factory.LazyAttribute(lambda obj: f"user_{obj.id}@example.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    password = Faker("password")
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

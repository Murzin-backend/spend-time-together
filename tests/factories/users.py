from datetime import datetime
from typing import Any

import factory
from factory import Factory, Faker

from app.core.users.models import Users


class UserFactory(Factory):
    class Meta:
        model = Users

    id = factory.Sequence(lambda n: n)
    login = factory.LazyAttribute(lambda obj: f"user_{obj.id}")
    email = factory.LazyAttribute(lambda obj: f"user_{obj.id}@example.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    password = Faker("password")
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

    @classmethod
    def create_batch_dict(cls, size: int, **kwargs: Any) -> list[dict]:
        return [vars(cls.build(**kwargs)) for _ in range(size)]

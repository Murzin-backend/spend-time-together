from factory.alchemy import SQLAlchemyModelFactory


class AsyncSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    """Асинхронная фабрика для SQLAlchemy."""
    class Meta:
        abstract = True

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        """Переопределяем метод _create для асинхронной работы."""
        session = cls._meta.sqlalchemy_session
        instance = model_class(*args, **kwargs)
        session.add(instance)
        if cls._meta.sqlalchemy_session_persistence == "flush":
            await session.flush()
        return instance

    @classmethod
    async def create_batch(cls, size, **kwargs):
        """Переопределяем create_batch для асинхронной работы."""
        return [await cls.create(**kwargs) for _ in range(size)]

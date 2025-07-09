import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool

from app.infra.adapters.database import Base
from app.core.users import models as users_models
from app.core.auth.models import UsersSession

from settings.database import Settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url():
    """Возвращает URL базы данных из настроек."""
    return Settings().DATABASE_URL


def run_migrations_offline() -> None:
    """Запуск миграций в 'офлайн' режиме.

    Этот скрипт настраивает контекст только с URL
    и target_metadata, без движка. Хотя здесь можно было бы
    сгенерировать SQL, мы пропустим это.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в 'онлайн' режиме.

    В этом сценарии нам нужно создать движок
    и связать соединение с контекстом.

    """
    connectable = create_async_engine(
        get_database_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
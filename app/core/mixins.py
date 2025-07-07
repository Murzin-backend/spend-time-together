from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.adapters.database import Database


@dataclass
class BaseRepository:
    """
    Базовый класс для всех репозиториев.
    Предоставляет доступ к объекту базы данных.
    """
    db: Database
from dataclasses import dataclass

from app.infra.adapters.database import Database


@dataclass
class BaseRepository:
    """
    Базовый класс для всех репозиториев.
    Предоставляет доступ к объекту базы данных.
    """
    db: Database
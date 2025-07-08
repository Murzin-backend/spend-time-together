# Управление миграциями с Alembic

Этот раздел содержит инструкции по работе с миграциями базы данных с помощью Alembic в рамках данного проекта.

Все команды выполняются внутри Docker-контейнера `web` для обеспечения корректного окружения и доступа к зависимостям.

## Создание новой миграции

После внесения изменений в модели SQLAlchemy (например, в `app/core/**/models.py`), необходимо сгенерировать новый файл миграции. Alembic проанализирует модели и автоматически создаст скрипт для обновления схемы базы данных.

```bash
docker-compose run --rm web poetry run alembic revision --autogenerate -m "Краткое описание миграции"
```

*   `--autogenerate`: указывает Alembic сравнить текущее состояние моделей с состоянием базы данных и сгенерировать изменения.
*   `-m "..."`: краткое сообщение, описывающее суть миграции.

Новый файл миграции будет создан в директории `migration/versions`.

## Применение миграций

### Обновление до последней версии

Чтобы применить все доступные миграции и обновить схему БД до последней версии, используйте команду `upgrade head`:

```bash
docker-compose run --rm web poetry run alembic upgrade head
```

Эта команда автоматически выполняется при каждом запуске контейнера `web`.

### Обновление до конкретной версии

Вы можете обновиться до конкретной ревизии, указав её идентификатор:

```bash
docker-compose run --rm web poetry run alembic upgrade <revision_id>
```

## Откат миграций

### Откат на одну ревизию назад

Для отката последней примененной миграции:

```bash
docker-compose run --rm web poetry run alembic downgrade -1
```

### Откат до конкретной версии

Для отката до определенной ревизии:

```bash
docker-compose run --rm web poetry run alembic downgrade <revision_id>
```

### Полный откат

Чтобы отменить все миграции, используйте `base`:

```bash
docker-compose run --rm web poetry run alembic downgrade base
```

## Просмотр информации

### Показать текущую ревизию

```bash
docker-compose run --rm web poetry run alembic current
```

### Показать историю миграций

```bash
docker-compose run --rm web poetry run alembic history
```

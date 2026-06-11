# bot/infrastructure/database/alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

# Импортируем Base и все модели
from infrastructure.database.base import Base
from infrastructure.database.models import User, Category, Product, Order
from settings.config import config as app_config

# Alembic Config object
config = context.config

# Берем URL из нашего конфига
config.set_main_option("sqlalchemy.url", app_config.database.dsn)

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для авто-генерации
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Offline режим (только SQL)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Online режим (реальное применение)"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск онлайн миграций"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
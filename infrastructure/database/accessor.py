"""
Accessor для PostgreSQL.

Создаёт асинхронный движок и фабрику сессий
на основе DatabaseConfig из settings.
"""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from settings.config import config

logger = logging.getLogger(__name__)

# Асинхронный движок
engine = create_async_engine(
    url=config.database.dsn,
    echo=False,  # True для отладки SQL-запросов
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Асинхронный генератор сессий (для Dependency Injection)"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_connection() -> bool:
    """Проверить подключение к БД"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection OK")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def close_engine() -> None:
    """Закрыть движок при остановке"""
    await engine.dispose()
    logger.info("Database engine disposed")
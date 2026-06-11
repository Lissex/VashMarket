# bot/infrastructure/database/repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from ..models import User


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, telegram_id: int, username: str = None, full_name: str = None) -> User:
        user = User(telegram_id=telegram_id, username=username, full_name=full_name)
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def update_orders_count(self, user_id: UUID) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(orders_count=User.orders_count + 1)
        )
    
    async def get_or_create(self, telegram_id: int, username: str = None, full_name: str = None) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.create(telegram_id, username, full_name)
        return user
# bot/infrastructure/database/repositories/order_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional
from ..models import Order
from ..models.order import OrderStatus


class OrderRepository:
    """Репозиторий для работы с заказами"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, order_data: dict) -> Order:
        order = Order(**order_data)
        self.session.add(order)
        await self.session.flush()
        return order
    
    async def get_pending_orders(self) -> List[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.is_confirmed_by_admin == False, Order.status == OrderStatus.PENDING)
            .options(selectinload(Order.user), selectinload(Order.product))
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_user(self, user_id: UUID) -> List[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.product))
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    async def confirm_by_admin(self, order_id: UUID, admin_telegram_id: int) -> Optional[Order]:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if order and order.can_confirm_by_admin:
            order.confirm_by_admin(admin_telegram_id)
            await self.session.flush()
            return order
        return None
# bot/application/use_cases/get_user_orders.py
from uuid import UUID
from typing import List, Dict, Any

from infrastructure.database.repositories import (
    UserRepository,
    OrderRepository
)


class GetUserOrdersUseCase:
    """Получение заказов пользователя"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        order_repo: OrderRepository
    ):
        self.user_repo = user_repo
        self.order_repo = order_repo
    
    async def execute(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Получить все заказы пользователя"""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        
        if not user:
            return []
        
        orders = await self.order_repo.get_by_user(user.id)
        
        return [
            {
                "id": order.id,
                "product_name": order.product.name if order.product else "Unknown",
                "quantity": order.quantity,
                "total_price": order.total_price,
                "formatted_price": f"{order.total_price:,.0f} ₽".replace(",", " "),
                "status": order.status,
                "status_text": order.status_text,
                "status_emoji": order.status_emoji,
                "is_confirmed_by_admin": order.is_confirmed_by_admin,
                "created_at": order.created_at,
                "confirmed_by_admin_at": order.confirmed_by_admin_at
            }
            for order in orders
        ]
# bot/application/use_cases/confirm_order.py
from uuid import UUID
from typing import Optional

from infrastructure.database.repositories import OrderRepository


class ConfirmOrderUseCase:
    """Подтверждение заказа админом"""
    
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo
    
    async def execute(self, order_id: UUID, admin_telegram_id: int) -> Optional[dict]:
        """
        Подтвердить заказ админом
        
        Returns:
            dict: заказ или None если не найден
        """
        order = await self.order_repo.confirm_by_admin(order_id, admin_telegram_id)
        
        if not order:
            return None
        
        return {
            "order": order,
            "user": order.user,
            "product": order.product
        }
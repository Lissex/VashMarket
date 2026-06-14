# bot/application/use_cases/get_pending_orders.py
from typing import List, Dict, Any

from infrastructure.database.repositories import OrderRepository


class GetPendingOrdersUseCase:
    """Получение заказов, ожидающих подтверждения админа"""
    
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo
    
    async def execute(self) -> List[Dict[str, Any]]:
        """Получить все неподтвержденные заказы"""
        orders = await self.order_repo.get_pending_orders()
        
        return [
            {
                "id": order.id,
                "user_telegram_id": order.user.telegram_id if order.user else None,
                "username": order.user.username if order.user else None,
                "product_name": order.product.name if order.product else "Unknown",
                "quantity": order.quantity,
                "total_price": order.total_price,
                "formatted_price": f"{order.total_price:,.0f} ₽".replace(",", " "),
                "customer_name": order.customer_name,
                "customer_phone": order.customer_phone,
                "customer_address": order.customer_address,
                "comment": order.comment,
                "created_at": order.created_at
            }
            for order in orders
        ]
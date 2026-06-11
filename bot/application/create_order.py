# bot/application/use_cases/create_order.py
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional

from infrastructure.database.repositories import (
    UserRepository,
    ProductRepository,
    OrderRepository
)
from infrastructure.database.models.order import OrderStatus


class CreateOrderUseCase:
    """Создание нового заказа"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        product_repo: ProductRepository,
        order_repo: OrderRepository
    ):
        self.user_repo = user_repo
        self.product_repo = product_repo
        self.order_repo = order_repo
    
    async def execute(
        self,
        telegram_id: int,
        product_id: UUID,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        customer_address: Optional[str] = None,
        comment: Optional[str] = None
    ) -> dict:
        """
        Создать заказ
        
        Returns:
            dict: {
                "order": Order,
                "product": Product,
                "user": User
            }
        """
        # 1. Получаем пользователя
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.user_repo.create(telegram_id)
        
        # 2. Получаем товар
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Товар не найден")
        
        if not product.is_in_stock:
            raise ValueError("Товара нет в наличии")
        
        # 3. Уменьшаем остаток
        await self.product_repo.reduce_stock(product_id, 1)
        
        # 4. Создаем заказ
        total_price = float(product.price)  # * quantity пока 1
        
        order_data = {
            "user_id": user.id,
            "product_id": product_id,
            "quantity": 1,
            "total_price": total_price,
            "status": OrderStatus.PENDING,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "customer_address": customer_address,
            "comment": comment,
            "is_confirmed_by_admin": False
        }
        
        order = await self.order_repo.create(order_data)
        
        # 5. Увеличиваем счетчик заказов пользователя
        await self.user_repo.update_orders_count(user.id)
        
        return {
            "order": order,
            "product": product,
            "user": user
        }
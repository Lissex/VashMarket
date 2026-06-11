# bot/domain/entities/order.py
from dataclasses import dataclass, field
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional
from ..value_objects.order_status import OrderStatus


@dataclass
class Order:
    """Сущность заказа"""
    id: UUID = field(default_factory=uuid4)
    user_id: UUID
    product_id: UUID
    status: OrderStatus = OrderStatus.PENDING
    quantity: int = 1
    total_price: float = 0
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    comment: Optional[str] = None
    is_confirmed_by_admin: bool = False
    confirmed_by_admin_at: Optional[datetime] = None
    confirmed_by_admin_telegram_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    @property
    def can_confirm_by_admin(self) -> bool:
        """Может ли админ подтвердить заказ"""
        return not self.is_confirmed_by_admin and self.status == OrderStatus.PENDING
    
    def confirm_by_admin(self, admin_telegram_id: int) -> None:
        """Админ подтверждает заказ"""
        if not self.can_confirm_by_admin:
            raise ValueError(f"Нельзя подтвердить заказ в статусе {self.status}")
        self.is_confirmed_by_admin = True
        self.confirmed_by_admin_at = datetime.now()
        self.confirmed_by_admin_telegram_id = admin_telegram_id
    
    def confirm(self) -> None:
        """Подтвердить заказ"""
        if not self.is_confirmed_by_admin:
            raise ValueError("Заказ должен быть подтвержден админом")
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Нельзя подтвердить заказ в статусе {self.status}")
        self.status = OrderStatus.CONFIRMED
        self.confirmed_at = datetime.now()
    
    def pay(self) -> None:
        """Оплатить"""
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError(f"Нельзя оплатить заказ в статусе {self.status}")
        self.status = OrderStatus.PAID
        self.paid_at = datetime.now()
    
    def ship(self) -> None:
        """Отправить"""
        if self.status != OrderStatus.PAID:
            raise ValueError(f"Нельзя отправить заказ в статусе {self.status}")
        self.status = OrderStatus.SHIPPED
        self.shipped_at = datetime.now()
    
    def complete(self) -> None:
        """Завершить"""
        if self.status != OrderStatus.SHIPPED:
            raise ValueError(f"Нельзя завершить заказ в статусе {self.status}")
        self.status = OrderStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def cancel(self) -> None:
        """Отменить"""
        if self.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            raise ValueError(f"Нельзя отменить заказ в статусе {self.status}")
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.now()
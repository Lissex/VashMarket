# bot/domain/value_objects/order_status.py
from enum import Enum


class OrderStatus(str, Enum):
    """Value Object для статуса заказа"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    @property
    def is_final(self) -> bool:
        """Финальный ли статус"""
        return self in [self.COMPLETED, self.CANCELLED]
    
    @property
    def can_transition_to(self, new_status: "OrderStatus") -> bool:
        """Можно ли перейти в новый статус"""
        transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PAID, OrderStatus.CANCELLED],
            OrderStatus.PAID: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
            OrderStatus.COMPLETED: [],
            OrderStatus.CANCELLED: [],
        }
        return new_status in transitions.get(self, [])
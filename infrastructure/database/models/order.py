# bot/infrastructure/database/models/order.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, BigInteger, Text, DateTime, Float, Boolean
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from ..base import Base

if TYPE_CHECKING:
    from .user import User
    from .product import Product


class OrderStatus(str, Enum):
    PENDING = "pending"          # Ожидает обработки
    CONFIRMED = "confirmed"      # Подтвержден админом
    PAID = "paid"                # Оплачен
    SHIPPED = "shipped"          # Отправлен
    COMPLETED = "completed"      # Выполнен
    CANCELLED = "cancelled"      # Отменен


class Order(Base):
    __tablename__ = "orders"
    
    # Внешние ключи
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Информация о заказе
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Информация о покупателе
    customer_name: Mapped[str] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    customer_address: Mapped[str] = mapped_column(Text, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Подтверждение админом
    is_confirmed_by_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    confirmed_by_admin_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_by_admin_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)  # telegram_id админа
    
    # Уведомления
    notified_to_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    notified_to_user: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Даты
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
    product: Mapped["Product"] = relationship("Product", lazy="selectin")
    
    @property
    def can_confirm_by_admin(self) -> bool:
        """Может ли админ подтвердить заказ"""
        return not self.is_confirmed_by_admin and self.status == OrderStatus.PENDING
    
    @property
    def can_cancel(self) -> bool:
        """Можно ли отменить заказ"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    @property
    def can_confirm(self) -> bool:
        """Можно ли подтвердить заказ (после админа)"""
        return self.is_confirmed_by_admin and self.status == OrderStatus.PENDING
    
    @property
    def can_pay(self) -> bool:
        """Можно ли оплатить заказ"""
        return self.status == OrderStatus.CONFIRMED
    
    @property
    def can_ship(self) -> bool:
        """Можно ли отправить заказ"""
        return self.status == OrderStatus.PAID
    
    @property
    def can_complete(self) -> bool:
        """Можно ли завершить заказ"""
        return self.status == OrderStatus.SHIPPED
    
    def confirm_by_admin(self, admin_telegram_id: int) -> None:
        """Админ подтверждает заказ"""
        if not self.can_confirm_by_admin:
            raise ValueError(f"Нельзя подтвердить заказ в статусе {self.status}")
        self.is_confirmed_by_admin = True
        self.confirmed_by_admin_at = datetime.now()
        self.confirmed_by_admin_id = admin_telegram_id
    
    def confirm(self) -> None:
        """Подтвердить заказ (после админа)"""
        if not self.can_confirm:
            raise ValueError(f"Нельзя подтвердить заказ. is_confirmed_by_admin={self.is_confirmed_by_admin}, status={self.status}")
        self.status = OrderStatus.CONFIRMED
        self.confirmed_at = datetime.now()
    
    def pay(self) -> None:
        """Отметить как оплаченный"""
        if not self.can_pay:
            raise ValueError(f"Нельзя оплатить заказ в статусе {self.status}")
        self.status = OrderStatus.PAID
        self.paid_at = datetime.now()
    
    def ship(self) -> None:
        """Отправить заказ"""
        if not self.can_ship:
            raise ValueError(f"Нельзя отправить заказ в статусе {self.status}")
        self.status = OrderStatus.SHIPPED
        self.shipped_at = datetime.now()
    
    def complete(self) -> None:
        """Завершить заказ"""
        if not self.can_complete:
            raise ValueError(f"Нельзя завершить заказ в статусе {self.status}")
        self.status = OrderStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def cancel(self) -> None:
        """Отменить заказ"""
        if not self.can_cancel:
            raise ValueError(f"Нельзя отменить заказ в статусе {self.status}")
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.now()
    
    @property
    def status_emoji(self) -> str:
        """Emoji для статуса заказа"""
        if not self.is_confirmed_by_admin:
            return "⏳"  # Ждет подтверждения админа
        emojis = {
            OrderStatus.PENDING: "⏳",
            OrderStatus.CONFIRMED: "✅",
            OrderStatus.PAID: "💰",
            OrderStatus.SHIPPED: "📦",
            OrderStatus.COMPLETED: "🎉",
            OrderStatus.CANCELLED: "❌",
        }
        return emojis.get(self.status, "❓")
    
    @property
    def status_text(self) -> str:
        """Текст статуса на русском"""
        if not self.is_confirmed_by_admin:
            return "⏳ Ожидает подтверждения администратора"
        texts = {
            OrderStatus.PENDING: "⏳ Ожидает обработки",
            OrderStatus.CONFIRMED: "✅ Подтвержден",
            OrderStatus.PAID: "💰 Оплачен",
            OrderStatus.SHIPPED: "📦 Отправлен",
            OrderStatus.COMPLETED: "🎉 Выполнен",
            OrderStatus.CANCELLED: "❌ Отменен",
        }
        return texts.get(self.status, "Неизвестно")
    
    @property
    def formatted_total_price(self) -> str:
        """Отформатированная итоговая цена"""
        return f"{self.total_price:,.0f} ₽".replace(",", " ")
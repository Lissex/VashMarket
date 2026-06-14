# bot/infrastructure/database/models/order.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, DateTime, Float, Boolean
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from ..base import Base

if TYPE_CHECKING:
    from .user import User
    from .product import Product


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    customer_name: Mapped[str] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    customer_address: Mapped[str] = mapped_column(Text, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    
    is_confirmed_by_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    confirmed_by_admin_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_by_admin_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    notified_to_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    notified_to_user: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user: Mapped["User"] = relationship("User", lazy="selectin")
    product: Mapped["Product"] = relationship("Product", lazy="selectin")
    
    @property
    def can_confirm_by_admin(self) -> bool:
        return not self.is_confirmed_by_admin and self.status == OrderStatus.PENDING
    
    @property
    def can_cancel(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    @property
    def status_emoji(self) -> str:
        if not self.is_confirmed_by_admin:
            return "⏳"
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
        return f"{self.total_price:,.0f} ₽".replace(",", " ")
    
    def confirm_by_admin(self, admin_telegram_id: int) -> None:
        if not self.can_confirm_by_admin:
            raise ValueError(f"Нельзя подтвердить заказ в статусе {self.status}")
        self.is_confirmed_by_admin = True
        self.confirmed_by_admin_at = datetime.now()
        self.confirmed_by_admin_id = admin_telegram_id
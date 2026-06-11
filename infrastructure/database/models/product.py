# bot/infrastructure/database/models/product.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from ..base import Base

if TYPE_CHECKING:
    from .category import Category
    from .order import Order


class Product(Base):
    __tablename__ = "products"
    
    # Основная информация
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Медиа
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    photo_file_id: Mapped[str] = mapped_column(String(255), nullable=True)  # Telegram file_id для быстрой отправки
    
    # Количество
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Внешние ключи
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
        lazy="selectin"
    )
    
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="product",
        lazy="selectin"
    )
    
    @property
    def is_in_stock(self) -> bool:
        """Есть ли товар в наличии"""
        return self.stock > 0
    
    @property
    def formatted_price(self) -> str:
        """Отформатированная цена"""
        return f"{self.price:,.0f} ₽".replace(",", " ")
    
    def reduce_stock(self, quantity: int = 1) -> bool:
        """Уменьшить количество товара при покупке"""
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def increase_stock(self, quantity: int = 1) -> None:
        """Увеличить количество товара (при возврате или пополнении)"""
        self.stock += quantity
# bot/infrastructure/database/models/product.py
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, Float, ForeignKey, Boolean, DateTime, func
from typing import List, Optional, TYPE_CHECKING
from ..base import Base

if TYPE_CHECKING:
    from .category import Category
    from .order import Order


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    photo_file_id: Mapped[str] = mapped_column(String(255), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="product")
    
    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0
    
    @property
    def formatted_price(self) -> str:
        return f"{self.price:,.0f} ₽".replace(",", " ")
    
    def reduce_stock(self, quantity: int = 1) -> bool:
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def increase_stock(self, quantity: int = 1) -> None:
        self.stock += quantity
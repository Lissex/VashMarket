# bot/infrastructure/database/models/category.py
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, String, Text, Integer, ForeignKey, func
from typing import List, Optional, TYPE_CHECKING
from ..base import Base

if TYPE_CHECKING:
    from .product import Product


class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True)
    products_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")
    
    @property
    def level(self) -> int:
        level = 0
        current = self
        while current.parent_id:
            level += 1
            break
        return level
    
    @property
    def full_path(self) -> str:
        parts = []
        current = self
        while current:
            parts.append(current.name)
            current = current.parent
        return " → ".join(reversed(parts))
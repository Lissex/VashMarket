# bot/infrastructure/database/models/category.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, ForeignKey
from typing import List, Optional, TYPE_CHECKING
from ..base import Base

if TYPE_CHECKING:
    from .product import Product


class Category(Base):
    __tablename__ = "categories"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    products_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side=[Base.id],
        back_populates="children",
        lazy="selectin"
    )
    
    children: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="parent",
        lazy="selectin"
    )
    
    products: Mapped[List["Product"]] = relationship(
        "Product", 
        back_populates="category",
        lazy="selectin"
    )
    
    @property
    def level(self) -> int:
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level
    
    @property
    def full_path(self) -> str:
        parts = []
        current = self
        while current:
            parts.append(current.name)
            current = current.parent
        return " → ".join(reversed(parts))
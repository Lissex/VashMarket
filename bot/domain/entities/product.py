# bot/domain/entities/product.py
from dataclasses import dataclass, field
from uuid import uuid4, UUID
from typing import Optional


@dataclass
class Product:
    """Сущность товара"""
    id: UUID = field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    price: float
    photo_url: Optional[str] = None
    photo_file_id: Optional[str] = None
    stock: int = 0
    is_active: bool = True
    category_id: UUID
    
    @property
    def is_in_stock(self) -> bool:
        """Есть ли товар в наличии"""
        return self.stock > 0
    
    @property
    def formatted_price(self) -> str:
        """Отформатированная цена"""
        return f"{self.price:,.0f} ₽".replace(",", " ")
    
    def reduce_stock(self, quantity: int = 1) -> bool:
        """Уменьшить количество товара"""
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def increase_stock(self, quantity: int = 1) -> None:
        """Увеличить количество товара"""
        self.stock += quantity
    
    def activate(self) -> None:
        """Активировать товар"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Деактивировать товар"""
        self.is_active = False